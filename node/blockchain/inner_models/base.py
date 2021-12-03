from enum import IntEnum
from typing import Any, Optional

from pydantic import BaseModel as PydanticBaseModel
from pydantic import root_validator
from pydantic.class_validators import prep_validators
from pydantic.validators import enum_member_validator, strict_int_validator

from node.blockchain.constants import JSON_CRYPTO_KWARGS
from node.core.exceptions import NotEnoughNestingError
from node.core.utils.collections import deep_get, deep_set, deep_update


class BaseModel(PydanticBaseModel):

    def dict(self, **kwargs):  # noqa: A003
        exclude = self.Config.exclude
        if exclude:
            deep_update(kwargs, {'exclude': exclude})

        return super().dict(**kwargs)

    def json(self, **kwargs):
        # Always serialize in cryptographic friendly manner
        return super().json(**dict(kwargs, **JSON_CRYPTO_KWARGS))

    @root_validator(pre=True)
    def enrich(cls, values):
        enrich = cls.Config.enrich
        if not enrich:
            return values

        for target, source in enrich.items():
            try:
                value = deep_get(values, source.split('.'))
                deep_set(values, target.split('.'), value)
            except NotEnoughNestingError:
                # TODO(dmu) MEDIUM: For some reason nested values are sometimes model instances.
                #                   Figure out and remove this workaround
                continue

        return values

    def __init__(self, **data: Any) -> None:
        if getattr(self.__config__, 'strict', False):
            self._transform_validators(data)
        super().__init__(**data)

    class Config:
        exclude: Optional[dict] = None
        exclude_crypto: Optional[dict] = None
        enrich: Optional[dict] = None
        allow_mutation = False
        strict = True

    def _transform_validators(self, data):
        for k, v in data.items():
            if isinstance(v, dict) or k not in self.__fields__:
                continue
            field = self.__fields__.get(k)
            if issubclass(field.type_, IntEnum):
                field.validators = prep_validators([strict_int_validator, enum_member_validator])

from typing import Optional

from pydantic import BaseModel as PydanticBaseModel
from pydantic import root_validator

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
        kwargs['separators'] = (',', ':')
        kwargs['sort_keys'] = True
        return super().json(**kwargs)

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

    class Config:
        exclude: Optional[dict] = None
        exclude_crypto: Optional[dict] = None
        enrich: Optional[dict] = None
        allow_mutation = False

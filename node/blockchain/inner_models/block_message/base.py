from datetime import datetime
from typing import Optional

from node.blockchain.inner_models.base import BaseModel
from node.blockchain.inner_models.mixins.message import MessageMixin
from node.blockchain.inner_models.signed_change_request import GenesisSignedChangeRequest, SignedChangeRequest
from node.core.utils.types import AccountNumber, BlockIdentifier, Type, intstr

from ..account_state import AccountState


class BlockMessageUpdate(BaseModel):
    accounts: dict[AccountNumber, AccountState]
    schedule: dict[intstr, AccountNumber]


class BlockMessage(BaseModel, MessageMixin):
    type: Type  # noqa: A003
    number: int
    identifier: Optional[BlockIdentifier]
    timestamp: datetime
    update: BlockMessageUpdate
    request: SignedChangeRequest

    @classmethod
    def parse_obj(cls, *args, **kwargs):
        obj = super().parse_obj(*args, **kwargs)
        type_ = obj.type
        class_ = TYPE_MAP.get(type_)
        if not class_:
            # TODO(dmu) MEDIUM: Raise validation error instead
            raise Exception(f'Unknown type: {type_}')

        if cls == class_:  # avoid recursion
            return obj

        return class_.parse_obj(*args, **kwargs)


class GenesisBlockMessage(BlockMessage):
    request: GenesisSignedChangeRequest


TYPE_MAP = {Type.GENESIS: GenesisBlockMessage}

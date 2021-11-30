from datetime import datetime
from typing import Optional
from typing import Type as TypingType
from typing import TypeVar

from node.blockchain.inner_models.base import BaseModel
from node.blockchain.inner_models.mixins.message import MessageMixin
from node.blockchain.inner_models.signed_change_request import (
    GenesisSignedChangeRequest, NodeDeclarationSignedChangeRequest, SignedChangeRequest
)
from node.core.utils.types import AccountNumber, BlockIdentifier, Type, intstr, AccountLock

from ..account_state import AccountState

T = TypeVar('T', bound='BlockMessage')
U = TypeVar('U', bound='BlockMessageUpdate')


class BlockMessageUpdate(BaseModel):
    accounts: dict[AccountNumber, AccountState]
    schedule: dict[intstr, AccountNumber]

    @classmethod
    def get_account_lock(cls, account_number: AccountNumber) -> AccountLock:
        raise NotImplementedError

    @classmethod
    def create_from_signed_change_request(cls: TypingType[U], request: SignedChangeRequest) -> U:
        raise NotImplementedError('Must be implemented in child classes')


class BlockMessage(BaseModel, MessageMixin):
    type: Type  # noqa: A003
    number: int
    identifier: Optional[BlockIdentifier]
    timestamp: datetime
    update: BlockMessageUpdate
    request: SignedChangeRequest

    @classmethod
    def create_from_signed_change_request(cls: TypingType[T], request: SignedChangeRequest) -> T:
        if isinstance(request, GenesisSignedChangeRequest):
            raise TypeError(
                'GenesisSignedChangeRequest is special since it does not contain all required information '
                'to construct a block message. Use GenesisBlockMessage.create_from_signed_change_request()'
            )

        from .type_map import TYPE_MAP
        class_ = TYPE_MAP.get(request.message.type)
        assert class_  # because message.type should be validated by now

        assert 'create_from_signed_change_request' in class_.__dict__, (
            f'create_from_signed_change_request() must be implemented in {class_}'
        )
        return class_.create_from_signed_change_request(request)

    @classmethod
    def parse_obj(cls, *args, **kwargs):
        obj = super().parse_obj(*args, **kwargs)
        type_ = obj.type
        from .type_map import TYPE_MAP
        class_ = TYPE_MAP.get(type_)
        assert class_  # because message.type should be validated by now

        if cls == class_:  # avoid recursion
            return obj

        return class_.parse_obj(*args, **kwargs)

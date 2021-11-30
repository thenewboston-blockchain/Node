from datetime import datetime
from typing import Optional
from typing import Type as TypingType
from typing import TypeVar

from node.blockchain.inner_models.base import BaseModel
from node.blockchain.inner_models.mixins.message import MessageMixin
from node.blockchain.inner_models.signed_change_request import (
    GenesisSignedChangeRequest, NodeDeclarationSignedChangeRequest, SignedChangeRequest
)
from node.core.utils.types import AccountNumber, BlockIdentifier, Type, intstr

from ..account_state import AccountState

T = TypeVar('T', bound='BlockMessage')


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
    def create_from_signed_change_request(cls: TypingType[T], request: SignedChangeRequest) -> T:
        if isinstance(request, GenesisSignedChangeRequest):
            raise TypeError(
                'GenesisSignedChangeRequest is special since it does not contain all required information '
                'to construct a block message. Use GenesisBlockMessage.create_from_signed_change_request()'
            )

        if isinstance(request, NodeDeclarationSignedChangeRequest):
            from .node_declaration import NodeDeclarationBlockMessage

            # TODO(dmu) MEDIUM: Automatically apply this assert to all subclasses of BlockMessage
            assert 'create_from_signed_change_request' in NodeDeclarationBlockMessage.__dict__
            return NodeDeclarationBlockMessage.create_from_signed_change_request(request=request)

        raise TypeError(f'Unknown type of {request}')

    @classmethod
    def parse_obj(cls, *args, **kwargs):
        obj = super().parse_obj(*args, **kwargs)
        type_ = obj.type
        from node.blockchain.inner_models.type_map import get_block_message_subclass
        class_ = get_block_message_subclass(type_)
        assert class_

        if cls == class_:  # avoid recursion
            return obj

        return class_.parse_obj(*args, **kwargs)

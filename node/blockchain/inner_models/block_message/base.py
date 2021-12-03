from datetime import datetime
from typing import Optional
from typing import Type as TypingType
from typing import TypeVar

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models.base import BaseModel
from node.blockchain.inner_models.mixins.message import MessageMixin
from node.blockchain.inner_models.signed_change_request import GenesisSignedChangeRequest, SignedChangeRequest
from node.core.utils.types import AccountNumber, BlockIdentifier, Type, intstr

from ..account_state import AccountState

T = TypeVar('T', bound='BlockMessage')


class BlockMessageUpdate(BaseModel):
    accounts: Optional[dict[AccountNumber, AccountState]]
    # TODO(dmu) MEDIUM: Consider removing `schedule` field since it will be equal to `null` in  most blocks
    #                   Or subclass `BlockMessageUpdate` for certain block types (genesis and schedule) and
    #                   have that field just there
    schedule: Optional[dict[intstr, AccountNumber]]


class BlockMessage(BaseModel, MessageMixin):
    type: Type  # noqa: A003
    number: int
    # TODO(dmu) HIGH: Make identifier not optional, so it is properly validated
    identifier: Optional[BlockIdentifier]
    timestamp: datetime
    update: BlockMessageUpdate
    request: SignedChangeRequest

    @classmethod
    def make_block_message_update(cls, request: SignedChangeRequest) -> BlockMessageUpdate:
        raise NotImplementedError('Must be implement in child class')

    @classmethod
    def create_from_signed_change_request(
        cls: TypingType[T],
        request: SignedChangeRequest,
        blockchain_facade: BlockchainFacade,
    ) -> T:
        now = datetime.utcnow()
        if isinstance(request, GenesisSignedChangeRequest):
            raise TypeError(
                'GenesisSignedChangeRequest is special since it does not contain all required information '
                'to construct a block message. Use GenesisBlockMessage.create_from_signed_change_request()'
            )

        from node.blockchain.inner_models.type_map import get_block_message_subclass
        class_ = get_block_message_subclass(request.get_type())

        number = blockchain_facade.get_next_block_number()
        identifier = blockchain_facade.get_next_block_identifier()
        update = class_.make_block_message_update(request)

        return class_(
            number=number,
            identifier=identifier,
            timestamp=now,
            request=request,
            update=update,
        )

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

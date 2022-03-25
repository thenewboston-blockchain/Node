from datetime import datetime
from typing import Optional
from typing import Type as TypingType
from typing import TypeVar

from pydantic import root_validator, validator

from node.blockchain.constants import BLOCK_LOCK
from node.blockchain.inner_models.base import BaseModel
from node.blockchain.mixins.crypto import SignableMixin
from node.blockchain.mixins.validatable import ValidatableMixin
from node.blockchain.utils.lock import lock
from node.core.exceptions import ValidationError
from node.core.utils.types import non_negative_intstr, positive_int

from ...types import AccountNumber, BlockIdentifier, Type
from ..account_state import AccountState
from ..signed_change_request import GenesisSignedChangeRequest, SignedChangeRequest

T = TypeVar('T', bound='BlockMessage')


class BlockMessageUpdate(BaseModel):
    accounts: Optional[dict[AccountNumber, AccountState]]
    # TODO(dmu) MEDIUM: Consider removing `schedule` field since it will be equal to `null` in most blocks
    #                   Or subclass `BlockMessageUpdate` for certain block types (genesis and schedule) and
    #                   have that field just there
    schedule: Optional[dict[non_negative_intstr, AccountNumber]]

    @root_validator
    def not_empty(cls, values):
        if not values['accounts'] and not values['schedule']:
            raise ValueError('Update must be not empty')
        return values


class BlockMessageType(BaseModel):
    type: Type  # noqa: A003


class BlockMessage(ValidatableMixin, BlockMessageType, SignableMixin):
    number: positive_int  # it is redefined in GenesisBlockMessage, so value 0 is allowed
    identifier: BlockIdentifier
    timestamp: datetime
    update: BlockMessageUpdate
    request: SignedChangeRequest

    @classmethod
    def make_block_message_update(cls, request: SignedChangeRequest, blockchain_facade) -> BlockMessageUpdate:
        raise NotImplementedError('Must be implement in child class')

    @classmethod
    def create_from_signed_change_request(
        cls: TypingType[T],
        request: SignedChangeRequest,
        blockchain_facade,
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
        if number == 0:
            raise ValueError(f'Block number 0 must be {Type.GENESIS.name}, got {request.get_type().name}')

        identifier = blockchain_facade.get_next_block_identifier()
        update = class_.make_block_message_update(request, blockchain_facade)

        return class_(
            number=number,
            identifier=identifier,
            timestamp=now,
            request=request,
            update=update,
        )

    @classmethod
    def parse_obj(cls, *args, **kwargs):
        if cls is not BlockMessage and issubclass(cls, BlockMessage):
            return super().parse_obj(*args, **kwargs)

        obj = BlockMessageType.parse_obj(*args, **kwargs)
        type_ = obj.type
        from node.blockchain.inner_models.type_map import get_block_message_subclass
        class_ = get_block_message_subclass(type_)
        assert class_
        return class_.parse_obj(*args, **kwargs)

    def validate_business_logic(self):
        self.request.validate_business_logic()

    def validate_number(self, blockchain_facade):
        if blockchain_facade.get_next_block_number() != self.number:
            raise ValidationError('Invalid block number')

    def validate_identifier(self, blockchain_facade):
        if blockchain_facade.get_next_block_identifier() != self.identifier:
            raise ValidationError('Invalid identifier')

    def validate_update(self, blockchain_facade):
        if self.update != self.make_block_message_update(self.request, blockchain_facade):
            raise ValidationError('Invalid update')

    @lock(BLOCK_LOCK, expect_locked=True)
    def validate_blockchain_state_dependent(self, blockchain_facade):
        self.request.validate_blockchain_state_dependent(blockchain_facade, bypass_lock_validation=True)
        self.validate_number(blockchain_facade)
        self.validate_identifier(blockchain_facade)
        self.validate_update(blockchain_facade)

    @validator('timestamp')
    def validate_timestamp(cls, value):
        if value.tzinfo is not None:
            raise ValidationError('Timestamp without timezone is expected')
        return value

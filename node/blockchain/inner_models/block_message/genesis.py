from datetime import datetime
from typing import Optional
from typing import Type as TypingType
from typing import TypeVar

from pydantic import Field

from node.blockchain.inner_models.account_state import AccountState
from node.blockchain.inner_models.node import Node
from node.blockchain.inner_models.signed_change_request import GenesisSignedChangeRequest
from node.core.exceptions import ValidationError

from ...types import BlockIdentifier, Type
from .base import BlockMessage, BlockMessageUpdate

GenesisBlockMessageT = TypeVar('GenesisBlockMessageT', bound='GenesisBlockMessage')


class GenesisBlockMessage(BlockMessage):
    number: int = Field(default=0, const=True)
    identifier: Optional[BlockIdentifier] = Field(default=None, const=True)  # type: ignore
    type: Type = Field(default=Type.GENESIS, const=True)  # noqa: A003
    request: GenesisSignedChangeRequest

    @classmethod
    def make_genesis_block_message_update(
        cls, request: GenesisSignedChangeRequest, primary_validator_node: Node
    ) -> BlockMessageUpdate:
        accounts = {}
        for account_number, alpha_account in request.message.accounts.items():
            accounts[account_number.lower()] = AccountState(
                # TODO(dmu) MEDIUM: Consider not storing account_lock if it is equal to account_number
                balance=alpha_account.balance,
                account_lock=alpha_account.balance_lock.lower()
            )

        primary_validator_node_identifier = primary_validator_node.identifier
        primary_validator_account_state = accounts.get(primary_validator_node_identifier)
        if primary_validator_account_state:
            primary_validator_account_state.node = primary_validator_node
        else:
            accounts[primary_validator_node_identifier] = AccountState(
                node=primary_validator_node, account_lock=primary_validator_node_identifier
            )

        schedule = {'0': primary_validator_node_identifier}

        return BlockMessageUpdate(
            accounts=accounts,
            schedule=schedule,
        )

    @classmethod
    def make_block_message_update(cls, request: GenesisSignedChangeRequest, blockchain_facade) -> BlockMessageUpdate:
        raise NotImplementedError(
            f'Genesis block is a special block therefore {cls.make_genesis_block_message_update.__name__}() method '
            f'must be used instead'
        )

    @classmethod
    def create_from_signed_change_request(  # type: ignore
        cls: TypingType[GenesisBlockMessageT], request: GenesisSignedChangeRequest, primary_validator_node: Node
    ) -> GenesisBlockMessageT:
        now = datetime.utcnow()
        update = cls.make_genesis_block_message_update(request, primary_validator_node)
        return cls(
            timestamp=now,
            request=request,
            update=update,
        )

    def validate_blockchain_state_dependent(self, blockchain_facade):
        super().validate_blockchain_state_dependent(blockchain_facade)
        if blockchain_facade.has_blocks():
            raise ValidationError('Blockchain must not have blocks')

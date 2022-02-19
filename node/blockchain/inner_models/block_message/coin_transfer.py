from pydantic import Field

from node.blockchain.inner_models import AccountState
from node.blockchain.inner_models.signed_change_request import CoinTransferSignedChangeRequest
from node.core.exceptions import ValidationError

from ...types import AccountNumber, Type
from .base import BlockMessage, BlockMessageUpdate


class CoinTransferBlockMessage(BlockMessage):
    type: Type = Field(default=Type.COIN_TRANSFER, const=True)  # noqa: A003
    request: CoinTransferSignedChangeRequest

    @classmethod
    def make_block_message_update(
        cls, request: CoinTransferSignedChangeRequest, blockchain_facade
    ) -> BlockMessageUpdate:
        return BlockMessageUpdate(
            accounts={
                **cls._make_sender_account_state(request, blockchain_facade),
                **cls._make_recipients_account_states(request, blockchain_facade),
            }
        )

    @classmethod
    def _make_sender_account_state(cls, request, blockchain_facade) -> dict[AccountNumber, AccountState]:
        sender_account = request.signer
        sender_balance = blockchain_facade.get_account_balance(sender_account)
        if (amount := request.message.get_total_amount()) > sender_balance:
            raise ValidationError(f'Sender account {sender_account} balance is not enough to send {amount} coins')

        return {sender_account: AccountState(balance=sender_balance - amount, account_lock=request.make_hash())}

    @classmethod
    def _make_recipients_account_states(cls, request, blockchain_facade) -> dict[AccountNumber, AccountState]:
        updated_amounts: dict[AccountNumber, int] = {}
        for transaction in request.message.txs:
            if (recipient := transaction.recipient) not in updated_amounts:
                updated_amounts[recipient] = blockchain_facade.get_account_balance(recipient)
            updated_amounts[recipient] += transaction.amount

        updated_account_states = {
            account_number: AccountState(balance=amount) for account_number, amount in updated_amounts.items()
        }
        return updated_account_states

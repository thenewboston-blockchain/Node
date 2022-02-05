from pydantic import Field

from node.blockchain.inner_models import AccountState
from node.blockchain.inner_models.signed_change_request import CoinTransferSignedChangeRequest
from node.core.exceptions import TransactionError

from ...types import AccountNumber, Type
from .base import BlockMessage, BlockMessageUpdate


class CoinTransferBlockMessage(BlockMessage):
    type: Type = Field(default=Type.COIN_TRANSFER, const=True)  # noqa: A003
    request: CoinTransferSignedChangeRequest

    @classmethod
    def make_block_message_update(cls, request: CoinTransferSignedChangeRequest) -> BlockMessageUpdate:
        from node.blockchain.facade import BlockchainFacade
        blockchain_facade = BlockchainFacade.get_instance()

        sender_account_states = cls._get_sender_account_states(request, blockchain_facade)
        recipient_account_states = cls._get_updated_account_states(request, blockchain_facade)

        updated_account_states: dict[AccountNumber, AccountState] = {
            **sender_account_states,
            **recipient_account_states,
        }

        return BlockMessageUpdate(accounts=updated_account_states)

    @classmethod
    def _get_sender_account_states(cls, request, blockchain_facade) -> dict[AccountNumber, AccountState]:
        coin_sender = request.signer
        transactions = request.message.txs

        sender_balance = blockchain_facade.get_account_balance(coin_sender)
        sent_amount = sum(tx.amount for tx in transactions)
        assert sent_amount > 0

        if sent_amount > sender_balance:
            raise TransactionError(
                f"Sender's account {coin_sender} has not enough balance to send {sent_amount} coins"
            )

        return {coin_sender: AccountState(balance=sender_balance - sent_amount, account_lock=request.make_hash())}

    @classmethod
    def _get_updated_account_states(cls, request, blockchain_facade) -> dict[AccountNumber, AccountState]:
        transactions = request.message.txs
        updated_amounts: dict[AccountNumber, int] = {}
        for transaction in transactions:
            recipient = transaction.recipient
            amount = transaction.amount

            updated_amounts.setdefault(recipient, blockchain_facade.get_account_balance(recipient))
            updated_amounts[recipient] += amount

        updated_account_states = {
            account_number: AccountState(balance=amount) for account_number, amount in updated_amounts.items()
        }
        return updated_account_states

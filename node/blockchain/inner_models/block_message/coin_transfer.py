from pydantic import Field

from node.blockchain.inner_models import AccountState
from node.blockchain.inner_models.signed_change_request import CoinTransferSignedChangeRequest

from ...types import Type
from .base import BlockMessage, BlockMessageUpdate


class CoinTransferBlockMessage(BlockMessage):
    type: Type = Field(default=Type.COIN_TRANSFER, const=True)  # noqa: A003
    request: CoinTransferSignedChangeRequest

    @classmethod
    def make_block_message_update(cls, request: CoinTransferSignedChangeRequest) -> BlockMessageUpdate:
        # TODO HIGH: Implement make_block_message_update method for CoinTransferBlockMessage
        #       https://thenewboston.atlassian.net/browse/BC-225
        account_state = AccountState()
        accounts = {request.signer: account_state}
        return BlockMessageUpdate(accounts=accounts)

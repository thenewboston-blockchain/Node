import pytest

from node.blockchain.inner_models.signed_change_request_message import (
    CoinTransferSignedChangeRequestMessage, CoinTransferTransaction
)
from node.blockchain.types import AccountLock


@pytest.fixture
def coin_transfer_signed_change_request_message(regular_node):
    return CoinTransferSignedChangeRequestMessage(
        account_lock=AccountLock(regular_node.identifier),
        txs=[
            CoinTransferTransaction(recipient='0' * 64, amount=3, is_fee=True, memo='message'),
        ]
    )

import pytest

from node.blockchain.inner_models.signed_change_request_message import (
    CoinTransferSignedChangeRequestMessage, CoinTransferTransaction
)
from node.blockchain.types import AccountLock


@pytest.fixture
def coin_transfer_signed_change_request_message(
    treasury_account_key_pair, regular_node_key_pair, primary_validator_key_pair
):
    return CoinTransferSignedChangeRequestMessage(
        account_lock=AccountLock(treasury_account_key_pair.public),
        txs=[
            CoinTransferTransaction(recipient=regular_node_key_pair.public, amount=100, is_fee=False, memo='message'),
            CoinTransferTransaction(
                recipient=primary_validator_key_pair.public, amount=5, is_fee=True, memo='message'
            ),
        ]
    )

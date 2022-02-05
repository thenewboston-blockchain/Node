import pytest

from node.blockchain.inner_models import AccountState, CoinTransferBlockMessage, CoinTransferSignedChangeRequest
from node.blockchain.inner_models.signed_change_request_message import (
    CoinTransferSignedChangeRequestMessage, CoinTransferTransaction
)
from node.blockchain.types import AccountLock
from node.core.exceptions import ValidationError


@pytest.mark.django_db
def test_sender_has_not_enough_balance(regular_node_key_pair):
    coin_transfer_signed_change_request_message = CoinTransferSignedChangeRequestMessage(
        account_lock=AccountLock(regular_node_key_pair.public),
        txs=[
            CoinTransferTransaction(recipient='0' * 64, amount=5, is_fee=False, memo='message'),
            CoinTransferTransaction(recipient='1' * 64, amount=3, is_fee=True, memo='message'),
        ]
    )
    request = CoinTransferSignedChangeRequest.create_from_signed_change_request_message(
        message=coin_transfer_signed_change_request_message,
        signing_key=regular_node_key_pair.private,
    )
    with pytest.raises(
        ValidationError, match=f'Sender account {regular_node_key_pair.public} balance is not enough to send 8 coins'
    ):
        CoinTransferBlockMessage.make_block_message_update(request)


@pytest.mark.usefixtures('base_blockchain')
def test_make_block_message_update(
    coin_transfer_signed_change_request_message, treasury_account_key_pair, treasury_amount, regular_node_key_pair,
    primary_validator_key_pair
):
    request = CoinTransferSignedChangeRequest.create_from_signed_change_request_message(
        message=coin_transfer_signed_change_request_message,
        signing_key=treasury_account_key_pair.private,
    )
    block_message_update = CoinTransferBlockMessage.make_block_message_update(request)

    assert block_message_update.accounts.get(request.signer) == AccountState(
        balance=treasury_amount - 105,
        account_lock=request.make_hash(),
    )
    assert block_message_update.accounts.get(regular_node_key_pair.public) == AccountState(balance=100)
    assert block_message_update.accounts.get(primary_validator_key_pair.public) == AccountState(balance=5)
    assert block_message_update.schedule is None

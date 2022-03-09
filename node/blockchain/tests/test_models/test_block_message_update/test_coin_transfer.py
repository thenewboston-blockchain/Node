import pytest

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import AccountState, CoinTransferBlockMessage, CoinTransferSignedChangeRequest
from node.blockchain.inner_models.signed_change_request_message import (
    CoinTransferSignedChangeRequestMessage, CoinTransferTransaction
)
from node.blockchain.types import AccountLock
from node.core.exceptions import ValidationError


@pytest.mark.django_db
def test_sender_has_not_enough_balance(regular_node_key_pair):
    signed_change_request_message = CoinTransferSignedChangeRequestMessage(
        account_lock=AccountLock(regular_node_key_pair.public),
        txs=[
            CoinTransferTransaction(recipient='0' * 64, amount=5, is_fee=False, memo='message'),
            CoinTransferTransaction(recipient='1' * 64, amount=3, is_fee=True, memo='message'),
        ]
    )
    request = CoinTransferSignedChangeRequest.create_from_signed_change_request_message(
        message=signed_change_request_message,
        signing_key=regular_node_key_pair.private,
    )
    with pytest.raises(
        ValidationError, match=f'Sender account {regular_node_key_pair.public} balance is not enough to send 8 coins'
    ):
        CoinTransferBlockMessage.make_block_message_update(request, BlockchainFacade.get_instance())


@pytest.mark.usefixtures('base_blockchain')
def test_make_block_message_update(
    treasure_coin_transfer_signed_change_request, treasury_amount, regular_node, self_node
):
    request = treasure_coin_transfer_signed_change_request
    block_message_update = CoinTransferBlockMessage.make_block_message_update(request, BlockchainFacade.get_instance())

    assert block_message_update.schedule is None

    accounts = block_message_update.accounts
    assert len(accounts) == 3
    assert accounts.get(request.signer) == AccountState(
        balance=treasury_amount - request.message.get_total_amount(),
        account_lock=request.make_hash(),
    )
    assert accounts.get(regular_node.identifier) == AccountState(balance=100)
    assert accounts.get(self_node.identifier) == AccountState(balance=4)

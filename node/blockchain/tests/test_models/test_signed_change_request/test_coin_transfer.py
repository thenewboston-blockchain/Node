import pytest

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import SignedChangeRequest
from node.blockchain.inner_models.signed_change_request.coin_transfer import CoinTransferSignedChangeRequest
from node.blockchain.inner_models.signed_change_request_message import (
    CoinTransferSignedChangeRequestMessage, CoinTransferTransaction
)
from node.core.exceptions import ValidationError


def test_create_from_coin_transfer_signed_change_request_message(
    coin_transfer_signed_change_request_message, treasury_account_key_pair
):
    signed_change_request = SignedChangeRequest.create_from_signed_change_request_message(
        message=coin_transfer_signed_change_request_message,
        signing_key=treasury_account_key_pair.private,
    )
    assert isinstance(signed_change_request, CoinTransferSignedChangeRequest)
    assert signed_change_request.message == coin_transfer_signed_change_request_message
    assert signed_change_request.signer == treasury_account_key_pair.public
    assert signed_change_request.signature == (
        '16fefa4441a2f877ecc2e08e7055dfc7ad1c9f4357ada4085dba76bbd37f7fd8'
        '77b18eb45f08ef3562d8029e740717c29a352421d7040cc1fae5b80308da2a09'
    )


def test_serialize_and_deserialize_coin_transfer(
    treasure_coin_transfer_signed_change_request, treasury_account_key_pair
):
    assert isinstance(treasure_coin_transfer_signed_change_request, CoinTransferSignedChangeRequest)
    serialized = treasure_coin_transfer_signed_change_request.json()
    deserialized = SignedChangeRequest.parse_raw(serialized)
    assert isinstance(deserialized, CoinTransferSignedChangeRequest)
    assert deserialized.signer == treasure_coin_transfer_signed_change_request.signer
    assert deserialized.signature == treasure_coin_transfer_signed_change_request.signature
    assert deserialized.message == treasure_coin_transfer_signed_change_request.message
    assert deserialized == treasure_coin_transfer_signed_change_request

    serialized2 = deserialized.json()
    assert serialized == serialized2


@pytest.mark.usefixtures('base_blockchain', 'as_primary_validator')
def test_coin_transfer(
    treasure_coin_transfer_signed_change_request, treasury_account_key_pair, regular_node_key_pair,
    primary_validator_key_pair, treasury_amount
):
    blockchain_facade = BlockchainFacade.get_instance()
    blockchain_facade.add_block_from_signed_change_request(treasure_coin_transfer_signed_change_request)

    assert blockchain_facade.get_account_balance(treasury_account_key_pair.public) == treasury_amount - 105
    assert blockchain_facade.get_account_balance(regular_node_key_pair.public) == 100
    assert blockchain_facade.get_account_balance(primary_validator_key_pair.public) == 5


@pytest.mark.usefixtures('base_blockchain')
def test_invalid_account_lock(treasury_account_key_pair):
    blockchain_facade = BlockchainFacade.get_instance()

    request = CoinTransferSignedChangeRequest.create_from_signed_change_request_message(
        message=CoinTransferSignedChangeRequestMessage(
            account_lock='0' * 64, txs=[CoinTransferTransaction(recipient='0' * 64, amount=10)]
        ),
        signing_key=treasury_account_key_pair.private,
    )
    with pytest.raises(ValidationError, match='Invalid account lock'):
        blockchain_facade.add_block_from_signed_change_request(request)


@pytest.mark.usefixtures('base_blockchain', 'as_primary_validator')
def test_validate_amount_when_balance_is_not_enough(
    treasure_coin_transfer_signed_change_request, regular_node_key_pair
):
    blockchain_facade = BlockchainFacade.get_instance()

    blockchain_facade.add_block_from_signed_change_request(treasure_coin_transfer_signed_change_request)
    assert blockchain_facade.get_account_balance(regular_node_key_pair.public) == 100

    signed_change_request_message = CoinTransferSignedChangeRequestMessage(
        account_lock='0' * 64, txs=[CoinTransferTransaction(recipient='0' * 64, amount=150)]
    )
    request = CoinTransferSignedChangeRequest.create_from_signed_change_request_message(
        message=signed_change_request_message,
        signing_key=regular_node_key_pair.private,
    )
    matched_message = 'Sender account 1c8e5f54a15b63a9f3d540ce505fd0799575ffeaac62ce625c917e6d915ea8bb ' \
                      'balance is not enough to send 150 coins'
    with pytest.raises(ValidationError, match=matched_message):
        blockchain_facade.add_block_from_signed_change_request(request)


@pytest.mark.usefixtures('base_blockchain', 'as_primary_validator')
def test_validate_circular_transactions(treasury_account_key_pair, regular_node_key_pair):
    blockchain_facade = BlockchainFacade.get_instance()

    signed_change_request_message = CoinTransferSignedChangeRequestMessage(
        account_lock=BlockchainFacade.get_instance().get_account_lock(treasury_account_key_pair.public),
        txs=[
            CoinTransferTransaction(recipient=regular_node_key_pair.public, amount=100),
            CoinTransferTransaction(recipient=treasury_account_key_pair.public, amount=100),
        ]
    )

    request = CoinTransferSignedChangeRequest.create_from_signed_change_request_message(
        message=signed_change_request_message,
        signing_key=treasury_account_key_pair.private,
    )

    with pytest.raises(ValidationError, match='Circular transactions detected'):
        blockchain_facade.add_block_from_signed_change_request(request)

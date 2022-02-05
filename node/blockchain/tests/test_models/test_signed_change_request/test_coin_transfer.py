import pytest

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import SignedChangeRequest
from node.blockchain.inner_models.signed_change_request.coin_transfer import CoinTransferSignedChangeRequest
from node.blockchain.inner_models.signed_change_request_message import CoinTransferSignedChangeRequestMessage
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
    coin_transfer_signed_change_request_message, treasury_account_key_pair
):
    signed_change_request = CoinTransferSignedChangeRequest.create_from_signed_change_request_message(
        message=coin_transfer_signed_change_request_message,
        signing_key=treasury_account_key_pair.private,
    )
    assert isinstance(signed_change_request, CoinTransferSignedChangeRequest)
    serialized = signed_change_request.json()
    deserialized = SignedChangeRequest.parse_raw(serialized)
    assert isinstance(deserialized, CoinTransferSignedChangeRequest)
    assert deserialized.signer == signed_change_request.signer
    assert deserialized.signature == signed_change_request.signature
    assert deserialized.message == signed_change_request.message
    assert deserialized == signed_change_request

    serialized2 = deserialized.json()
    assert serialized == serialized2


@pytest.mark.django_db
def test_invalid_account_lock(regular_node_key_pair):
    blockchain_facade = BlockchainFacade.get_instance()

    coin_transfer_signed_change_request_message = CoinTransferSignedChangeRequestMessage(account_lock='0' * 64, txs=[])
    request = CoinTransferSignedChangeRequest.create_from_signed_change_request_message(
        message=coin_transfer_signed_change_request_message,
        signing_key=regular_node_key_pair.private,
    )
    with pytest.raises(ValidationError, match='Invalid account lock'):
        blockchain_facade.add_block_from_signed_change_request(request)

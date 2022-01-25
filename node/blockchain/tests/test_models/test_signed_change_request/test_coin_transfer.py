import pytest

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import SignedChangeRequest
from node.blockchain.inner_models.signed_change_request.coin_transfer import CoinTransferSignedChangeRequest
from node.blockchain.inner_models.signed_change_request_message import CoinTransferSignedChangeRequestMessage
from node.blockchain.models.block.model import Block
from node.core.exceptions import ValidationError


def test_create_from_coin_transfer_signed_change_request_message(
    coin_transfer_signed_change_request_message, regular_node_key_pair
):
    signed_change_request = SignedChangeRequest.create_from_signed_change_request_message(
        message=coin_transfer_signed_change_request_message,
        signing_key=regular_node_key_pair.private,
    )
    assert isinstance(signed_change_request, CoinTransferSignedChangeRequest)
    assert signed_change_request.message == coin_transfer_signed_change_request_message
    assert signed_change_request.signer == regular_node_key_pair.public
    assert signed_change_request.signature == (
        '40d66503370e3d603c3c53654acabeb28a12be467b99967b2b37d146f859e4a8'
        '1f23dc6d148b6206f33e9269b27d821b4e2d922f94c3ea1e28107677be508a05'
    )


def test_serialize_and_deserialize_coin_transfer(coin_transfer_signed_change_request_message, regular_node_key_pair):
    signed_change_request = CoinTransferSignedChangeRequest.create_from_signed_change_request_message(
        message=coin_transfer_signed_change_request_message,
        signing_key=regular_node_key_pair.private,
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
        Block.objects.add_block_from_signed_change_request(request, blockchain_facade)

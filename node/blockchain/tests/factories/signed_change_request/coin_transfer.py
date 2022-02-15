from node.blockchain.inner_models import CoinTransferSignedChangeRequest
from node.blockchain.types import KeyPair

from ..signed_change_request_message.coin_transfer import make_coin_transfer_signed_change_request_message


def make_coin_transfer_signed_change_request(
    sender: KeyPair, recipient: KeyPair, primary_validator: KeyPair
) -> CoinTransferSignedChangeRequest:
    signed_change_request_message = make_coin_transfer_signed_change_request_message(
        sender.public, recipient.public, primary_validator.public
    )
    signed_change_request = CoinTransferSignedChangeRequest.create_from_signed_change_request_message(
        message=signed_change_request_message,
        signing_key=sender.private,
    )
    assert signed_change_request.message
    assert signed_change_request.signer
    assert signed_change_request.signature

    return signed_change_request

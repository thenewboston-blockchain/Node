from node.blockchain.inner_models import CoinTransferSignedChangeRequest
from node.blockchain.types import AccountNumber, KeyPair

from ..signed_change_request_message.coin_transfer import make_coin_transfer_signed_change_request_message


def make_coin_transfer_signed_change_request(
    sender_key_pair: KeyPair, recipient_account: AccountNumber, node_account: AccountNumber
) -> CoinTransferSignedChangeRequest:
    signed_change_request_message = make_coin_transfer_signed_change_request_message(
        sender_key_pair.public, recipient_account, node_account
    )
    signed_change_request = CoinTransferSignedChangeRequest.create_from_signed_change_request_message(
        message=signed_change_request_message,
        signing_key=sender_key_pair.private,
    )
    assert signed_change_request.message
    assert signed_change_request.signer
    assert signed_change_request.signature

    return signed_change_request

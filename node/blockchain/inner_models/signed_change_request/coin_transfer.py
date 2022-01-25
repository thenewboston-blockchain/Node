from ..signed_change_request_message import CoinTransferSignedChangeRequestMessage
from .base import SignedChangeRequest


class CoinTransferSignedChangeRequest(SignedChangeRequest):
    message: CoinTransferSignedChangeRequestMessage

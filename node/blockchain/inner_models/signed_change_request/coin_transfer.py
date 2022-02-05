from ..signed_change_request_message import CoinTransferSignedChangeRequestMessage
from .base import SignedChangeRequest


class CoinTransferSignedChangeRequest(SignedChangeRequest):
    message: CoinTransferSignedChangeRequestMessage

    def validate_business_logic(self):
        super().validate_business_logic()
        # TODO(dmu) CRITICAL: Implement in https://thenewboston.atlassian.net/browse/BC-217

    def validate_blockchain_state_dependent(self, blockchain_facade):
        super().validate_blockchain_state_dependent(blockchain_facade)
        # TODO(dmu) CRITICAL: Implement in https://thenewboston.atlassian.net/browse/BC-217

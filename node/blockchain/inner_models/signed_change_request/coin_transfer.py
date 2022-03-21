from node.core.exceptions import ValidationError

from ..signed_change_request_message import CoinTransferSignedChangeRequestMessage
from .base import SignedChangeRequest


class CoinTransferSignedChangeRequest(SignedChangeRequest):
    message: CoinTransferSignedChangeRequestMessage

    def validate_business_logic(self):
        super().validate_business_logic()
        self.validate_circular_transactions()

    def validate_blockchain_state_dependent(self, blockchain_facade):
        super().validate_blockchain_state_dependent(blockchain_facade)
        self.validate_amount(blockchain_facade)

    def validate_circular_transactions(self):
        if self.signer in (tx.recipient for tx in self.message.txs):
            raise ValidationError('Circular transactions detected')

    def validate_amount(self, blockchain_facade):
        if blockchain_facade.get_account_balance(self.signer) < self.message.get_total_amount():
            raise ValidationError('Signer balance mast be greater than total amount')

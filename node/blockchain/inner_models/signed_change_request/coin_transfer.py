from django.conf import settings

from node.core.exceptions import ValidationError
from node.core.utils.cryptography import get_node_identifier

from ..signed_change_request_message import CoinTransferSignedChangeRequestMessage
from .base import SignedChangeRequest


class CoinTransferSignedChangeRequest(SignedChangeRequest):
    message: CoinTransferSignedChangeRequestMessage

    def validate_business_logic(self):
        super().validate_business_logic()
        self.validate_circular_transactions()
        self.validate_node_fee()

    def validate_blockchain_state_dependent(self, blockchain_facade):
        super().validate_blockchain_state_dependent(blockchain_facade)
        self.validate_amount(blockchain_facade)

    def validate_circular_transactions(self):
        if self.signer in (tx.recipient for tx in self.message.txs):
            raise ValidationError('Circular transactions detected')

    def validate_node_fee(self):
        node_identifier = get_node_identifier()
        if self.signer != node_identifier and self.message.get_total_amount_by_recipient(
            node_identifier, True
        ) < settings.NODE_FEE:
            raise ValidationError('Fee amount is not enough')

    def validate_amount(self, blockchain_facade):
        if blockchain_facade.get_account_balance(self.signer) < self.message.get_total_amount():
            raise ValidationError('Signer balance mast be greater than total amount')

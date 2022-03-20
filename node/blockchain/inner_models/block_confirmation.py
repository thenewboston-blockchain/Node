from pydantic import root_validator

from node.blockchain.mixins.crypto import SignableMixin, validate_signature_helper
from node.blockchain.mixins.validatable import ValidatableMixin
from node.core.exceptions import ValidationError
from node.core.utils.cryptography import derive_public_key
from node.core.utils.types import non_negative_int

from ..types import AccountNumber, Hash, Signature
from .base import BaseModel


class BlockConfirmationMessage(BaseModel, SignableMixin):
    number: non_negative_int
    hash: Hash  # noqa: A003


class BlockConfirmation(ValidatableMixin, BaseModel):
    signer: AccountNumber
    signature: Signature
    message: BlockConfirmationMessage

    @classmethod
    def create(cls, number, hash_, signing_key):
        message = BlockConfirmationMessage(number=number, hash=hash_)
        signer = derive_public_key(signing_key)
        signature = message.make_signature(signing_key)

        return cls(signer=signer, signature=signature, message=message)

    @root_validator
    def validate_signature(cls, values):
        return validate_signature_helper(values)

    def get_number(self):
        return self.message.number

    def get_hash(self):
        return self.message.hash

    def validate_signer(self, blockchain_facade):
        if not blockchain_facade.has_blocks():
            return

        if not blockchain_facade.is_confirmation_validator(self.signer):
            raise ValidationError('Invalid block signer')

    def validate_number(self, blockchain_facade):
        if blockchain_facade.get_next_block_number() != self.get_number():
            raise ValidationError('Invalid block number')

    def validate_business_logic(self):
        pass

    def validate_blockchain_state_dependent(self, blockchain_facade):
        self.validate_signer(blockchain_facade)
        self.validate_number(blockchain_facade)

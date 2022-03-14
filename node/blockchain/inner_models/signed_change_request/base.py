from typing import Type as TypingType
from typing import TypeVar, cast

from pydantic import root_validator

from node.blockchain.constants import BLOCK_LOCK
from node.blockchain.mixins.crypto import HashableMixin, validate_signature_helper
from node.blockchain.mixins.validatable import ValidatableMixin
from node.blockchain.utils.lock import lock
from node.core.exceptions import ValidationError
from node.core.utils.cryptography import derive_public_key

from ...types import AccountNumber, Signature, SigningKey
from ..base import BaseModel
from ..signed_change_request_message import SignedChangeRequestMessage

T = TypeVar('T', bound='SignedChangeRequest')


class SignedChangeRequest(ValidatableMixin, BaseModel, HashableMixin):
    signer: AccountNumber
    signature: Signature
    message: SignedChangeRequestMessage

    @classmethod
    def create_from_signed_change_request_message(
        cls: TypingType[T], message: SignedChangeRequestMessage, signing_key: SigningKey
    ) -> T:
        from node.blockchain.inner_models.type_map import get_signed_change_request_subclass
        class_ = get_signed_change_request_subclass(message.type)
        assert class_  # because message.type should be validated by now
        class_ = cast(TypingType[T], class_)

        return class_(
            signer=derive_public_key(signing_key),
            signature=message.make_signature(signing_key),
            message=message,
        )

    @classmethod
    def parse_obj(cls, *args, **kwargs):
        obj = super().parse_obj(*args, **kwargs)
        type_ = obj.message.type
        from node.blockchain.inner_models.type_map import get_signed_change_request_subclass
        class_ = get_signed_change_request_subclass(type_)
        assert class_  # because message.type should be validated by now

        if cls == class_:  # avoid recursion
            return obj

        return class_.parse_obj(*args, **kwargs)

    @root_validator
    def validate_signature(cls, values):
        if cls == SignedChangeRequest:  # only child classes signature validation makes sense
            return values

        return validate_signature_helper(values)

    def validate_business_logic(self):
        self.message.validate_business_logic()

    def validate_account_lock(self, blockchain_facade):
        if blockchain_facade.get_account_lock(self.signer) != self.message.account_lock:
            raise ValidationError('Invalid account lock')

    @lock(BLOCK_LOCK, expect_locked=True)
    def validate_blockchain_state_dependent(self, blockchain_facade):
        self.message.validate_blockchain_state_dependent(blockchain_facade)
        self.validate_account_lock(blockchain_facade)

    def get_type(self):
        return self.message.type

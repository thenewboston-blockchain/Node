import logging

from node.blockchain.types import Hash, SigningKey
from node.core.utils.cryptography import generate_signature, hash_binary_data, is_signature_valid

logger = logging.getLogger(__name__)


def validate_signature_helper(values: dict):
    signer = values.get('signer')
    message = values.get('message')
    signature = values.get('signature')

    if (
        # TODO(dmu) MEDIUM: How is it possible that signer, signature, message can be empty?
        not signer or not signature or not message or
        not is_signature_valid(signer, message.make_binary_representation_for_cryptography(), signature)
    ):
        # TODO(dmu) LOW: Pydantic does not recognize custom ValidationError. Fix?
        raise ValueError('Invalid signature')


class CryptoAuxiliaryMixin:

    def make_binary_representation_for_cryptography(self) -> bytes:
        exclude_crypto = self.Config.exclude_crypto  # type: ignore
        kwargs = {'exclude': exclude_crypto} if exclude_crypto else {}
        return self.json(**kwargs).encode('utf-8')  # type: ignore


class HashableMixin(CryptoAuxiliaryMixin):

    def make_hash(self) -> Hash:
        normalized_message = self.make_binary_representation_for_cryptography()
        message_hash = hash_binary_data(normalized_message)
        return message_hash


class SignableMixin(CryptoAuxiliaryMixin):

    def make_signature(self, signing_key: SigningKey):
        _, signature = self.make_binary_representation_and_signature(signing_key)
        return signature

    def make_binary_representation_and_signature(self, signing_key: SigningKey):
        binary_representation = self.make_binary_representation_for_cryptography()
        return binary_representation, generate_signature(signing_key, binary_representation)


class SignableStringWrapper(str, SignableMixin):

    def make_binary_representation_for_cryptography(self) -> bytes:
        return self.encode('utf-8')  # type: ignore


class HashableStringWrapper(str, HashableMixin):

    def make_binary_representation_for_cryptography(self) -> bytes:
        return self.encode('utf-8')  # type: ignore

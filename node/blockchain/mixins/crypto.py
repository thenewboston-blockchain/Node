import logging

from node.blockchain.types import Hash, SigningKey
from node.core.utils.cryptography import generate_signature, hash_binary_data

logger = logging.getLogger(__name__)


class CryptoAuxiliaryMixin:

    def make_binary_message_for_cryptography(self) -> bytes:
        exclude_crypto = self.Config.exclude_crypto  # type: ignore
        kwargs = {'exclude': exclude_crypto} if exclude_crypto else {}
        return self.json(**kwargs).encode('utf-8')  # type: ignore


class HashableMixin(CryptoAuxiliaryMixin):

    def make_hash(self) -> Hash:
        normalized_message = self.make_binary_message_for_cryptography()
        message_hash = hash_binary_data(normalized_message)
        logger.debug('Got %s hash for message: %r', message_hash, normalized_message)
        return message_hash


class SignableMixin(CryptoAuxiliaryMixin):

    def make_signature(self, signing_key: SigningKey):
        _, signature = self.make_binary_data_and_signature(signing_key)
        return signature

    def make_binary_data_and_signature(self, signing_key: SigningKey):
        binary_data = self.make_binary_message_for_cryptography()
        return binary_data, generate_signature(signing_key, binary_data)


class SignableStringWrapper(str, SignableMixin):

    def make_binary_message_for_cryptography(self) -> bytes:
        return self.encode('utf-8')  # type: ignore


class HashableStringWrapper(str, HashableMixin):

    def make_binary_message_for_cryptography(self) -> bytes:
        return self.encode('utf-8')  # type: ignore

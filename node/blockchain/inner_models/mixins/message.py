import logging

from node.core.utils.cryptography import generate_signature, hash_binary_data
from node.core.utils.types import Hash, SigningKey

logger = logging.getLogger(__name__)


class MessageMixin:

    def get_binary_data_for_cryptography(self) -> bytes:
        return self.json(separators=(',', ':'), sort_keys=True).encode('utf-8')  # type: ignore

    def get_hash(self) -> Hash:
        normalized_message = self.get_binary_data_for_cryptography()
        message_hash = hash_binary_data(normalized_message)
        logger.debug('Got %s hash for message: %r', message_hash, normalized_message)
        return message_hash

    def get_signature(self, signing_key: SigningKey):
        _, signature = self.get_binary_data_and_signature(signing_key)
        return signature

    def get_binary_data_and_signature(self, signing_key: SigningKey):
        binary_data = self.get_binary_data_for_cryptography()
        return binary_data, generate_signature(signing_key, binary_data)

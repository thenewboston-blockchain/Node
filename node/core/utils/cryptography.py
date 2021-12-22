import json
from hashlib import sha3_256

from django.conf import settings
from nacl.exceptions import CryptoError
from nacl.signing import SigningKey as NaClSigningKey
from nacl.signing import VerifyKey

from .misc import bytes_to_hex, hex_to_bytes
from .types import AccountNumber, Hash, KeyPair, Signature, SigningKey


def generate_signature(signing_key: SigningKey, message: bytes) -> Signature:
    return NaClSigningKey(hex_to_bytes(signing_key)).sign(message).signature.hex()


def derive_public_key(signing_key: SigningKey) -> AccountNumber:
    return AccountNumber(bytes_to_hex(NaClSigningKey(hex_to_bytes(signing_key)).verify_key))


def normalize_dict(dict_: dict) -> bytes:
    return json.dumps(dict_, separators=(',', ':'), sort_keys=True).encode('utf-8')


def hash_binary_data(binary_data: bytes) -> Hash:
    return Hash(sha3_256(binary_data).digest().hex())


def get_signing_key():
    return settings.NODE_SIGNING_KEY


def get_node_identifier():
    return derive_public_key(get_signing_key())


def is_signature_valid(verify_key: AccountNumber, message: bytes, signature: Signature) -> bool:
    try:
        verify_key_bytes = hex_to_bytes(verify_key)
        signature_bytes = hex_to_bytes(signature)
    except ValueError:
        return False

    try:
        VerifyKey(verify_key_bytes).verify(message, signature_bytes)
    except CryptoError:
        return False

    return True


def generate_key_pair() -> KeyPair:
    signing_key = NaClSigningKey.generate()
    return KeyPair(bytes_to_hex(signing_key.verify_key), bytes_to_hex(signing_key))

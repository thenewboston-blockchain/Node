import json
from hashlib import sha3_256

from django.conf import settings
from nacl.signing import SigningKey as NaClSigningKey

from .misc import bytes_to_hex, hex_to_bytes
from .types import AccountNumber, Hash, Signature, SigningKey


def generate_signature(signing_key: SigningKey, message: bytes) -> Signature:
    return NaClSigningKey(hex_to_bytes(signing_key)).sign(message).signature.hex()


def derive_public_key(signing_key: SigningKey) -> AccountNumber:
    return AccountNumber(bytes_to_hex(NaClSigningKey(hex_to_bytes(signing_key)).verify_key))


def normalize_dict(dict_: dict) -> bytes:
    return json.dumps(dict_, separators=(',', ':'), sort_keys=True).encode('utf-8')


def hash_binary_data(binary_data: bytes) -> Hash:
    return Hash(sha3_256(binary_data).digest().hex())


def get_signing_key():
    return settings.SIGNING_KEY

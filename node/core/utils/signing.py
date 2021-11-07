import os

from nacl.encoding import HexEncoder
from nacl.signing import SigningKey, VerifyKey

from .tools import sort_and_encode


def encode_key(*, key: VerifyKey) -> str:
    """
    Return the hexadecimal representation of the binary public key data
    """

    if not isinstance(key, VerifyKey):
        raise RuntimeError('key must be of type nacl.signing.VerifyKey')

    return key.encode(encoder=HexEncoder).decode('utf-8')


def generate_signature(*, message: dict) -> str:
    """
    Sign message using signing key and return signature
    """
    encode_message = sort_and_encode(message)

    return get_signing_key().sign(encode_message).signature.hex()


def get_public_key() -> VerifyKey:
    """
    Return the public key from the signing key
    """

    return get_signing_key().verify_key


def get_signing_key() -> SigningKey:
    """
    Return signing key
    """

    network_signing_key = os.getenv('NODE_SIGNING_KEY')
    return SigningKey(network_signing_key, encoder=HexEncoder)


def verify_signature(*, message: bytes, signature: str, signer: str) -> None:
    """
    Verify block signature
    """

    verify_key = VerifyKey(signer.encode('utf-8'), encoder=HexEncoder)
    signature_bytes = bytes.fromhex(signature)
    verify_key.verify(message, signature_bytes)

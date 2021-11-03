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

    signing_key = get_signing_key()
    message = sort_and_encode(message)

    return signing_key.sign(message).signature.hex()


def get_public_key() -> VerifyKey:
    """
    Return the public key from the signing key
    """

    signing_key = get_signing_key()
    return signing_key.verify_key


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

    signer = VerifyKey(signer.encode('utf-8'), encoder=HexEncoder)
    signature = bytes.fromhex(signature)
    signer.verify(message, signature)

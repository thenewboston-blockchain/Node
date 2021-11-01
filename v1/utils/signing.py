import os

from nacl.encoding import HexEncoder
from nacl.signing import SigningKey, VerifyKey


def encode_key(*, key):
    """
    Return the hexadecimal representation of the binary public key data
    """

    if not isinstance(key, VerifyKey):
        raise RuntimeError('key must be of type nacl.signing.VerifyKey')

    return key.encode(encoder=HexEncoder).decode('utf-8')


def generate_signature(*, message, signing_key):
    """
    Sign message using signing key and return signature
    """

    return signing_key.sign(message).signature.hex()


def get_public_key(*, signing_key):
    """
    Return the public key from the signing key
    """

    if not isinstance(signing_key, SigningKey):
        raise RuntimeError('signing_key must be of type nacl.signing.SigningKey')

    return signing_key.verify_key


def get_signing_key():
    """
    Return signing key
    """

    network_signing_key = os.getenv('NODE_SIGNING_KEY')
    return SigningKey(network_signing_key, encoder=HexEncoder)


def verify_signature(*, message, signature, signer):
    """
    Verify block signature
    """

    signer = VerifyKey(signer.encode('utf-8'), encoder=HexEncoder)
    signature = bytes.fromhex(signature)
    signer.verify(message, signature)

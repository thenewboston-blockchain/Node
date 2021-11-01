from v1.utils.tools import sort_and_encode
from .signing import encode_key, generate_signature, get_public_key


def generate_block(*, message, signing_key):
    signature = generate_signature(
        message=sort_and_encode(message),
        signing_key=signing_key
    )

    public_key = get_public_key(signing_key=signing_key)

    block = {
        'message': message,
        'signature': signature,
        'signer': encode_key(key=public_key),
    }

    return block

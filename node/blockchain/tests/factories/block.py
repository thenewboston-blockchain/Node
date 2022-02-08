from node.blockchain.inner_models import Block
from node.core.utils.cryptography import derive_public_key


def make_block(block_message, signing_key):
    return Block(
        signer=derive_public_key(signing_key),
        signature=block_message.make_signature(signing_key),
        message=block_message
    )

from node.blockchain.inner_models import Block
from node.core.utils.cryptography import derive_public_key


def make_block(block_message, signing_key, block_class=Block):
    # TODO(dmu) MEDIUM: Derive block_class from block_message type
    return block_class(
        signer=derive_public_key(signing_key),
        signature=block_message.make_signature(signing_key),
        message=block_message
    )

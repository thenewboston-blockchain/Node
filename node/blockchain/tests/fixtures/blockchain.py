import pytest

from node.blockchain.facade import BlockchainFacade
from node.blockchain.models import Block


@pytest.fixture
def base_blockchain(genesis_block_message, primary_validator_key_pair, db):
    blockchain_facade = BlockchainFacade.get_instance()
    Block.objects.add_block_from_block_message(
        message=genesis_block_message,
        blockchain_facade=blockchain_facade,
        signing_key=primary_validator_key_pair.private,
        validate=False,
    )
    yield

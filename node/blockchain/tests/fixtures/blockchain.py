import pytest

from node.blockchain.facade import BlockchainFacade


@pytest.fixture
def base_blockchain(genesis_block_message, primary_validator_key_pair, db):
    BlockchainFacade.get_instance().add_block_from_block_message(
        message=genesis_block_message,
        signing_key=primary_validator_key_pair.private,
        validate=False,
    )


@pytest.fixture
def rich_blockchain(
    base_blockchain,
    primary_validator_key_pair,
    self_node_key_pair,
    regular_node_declaration_signed_change_request,
    self_node_declaration_signed_change_request,
):
    blockchain_facade = BlockchainFacade.get_instance()

    blockchain_facade.add_block_from_signed_change_request(
        signed_change_request=regular_node_declaration_signed_change_request,
        signing_key=primary_validator_key_pair.private,
        validate=False,
    )

    blockchain_facade.add_block_from_signed_change_request(
        signed_change_request=self_node_declaration_signed_change_request,
        signing_key=self_node_key_pair.private,
        validate=False,
    )
    # TODO(dmu) MEDIUM: Add more blocks as new block types are developed

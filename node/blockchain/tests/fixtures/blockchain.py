import pytest

from node.blockchain.facade import BlockchainFacade
from node.blockchain.tests.factories.node import make_node
from node.blockchain.tests.factories.signed_change_request.node_declaration import (
    make_node_declaration_signed_change_request
)
from node.blockchain.tests.factories.signed_change_request.pv_schedule_update import (
    make_pv_schedule_update_signed_change_request
)
from node.core.utils.cryptography import generate_key_pair


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
    confirmation_validator_key_pair,
    confirmation_validator_key_pair_2,
    regular_node_declaration_signed_change_request,
    self_node_declaration_signed_change_request,
    confirmation_validator_declaration_signed_change_request,
    confirmation_validator_2_declaration_signed_change_request,
):
    blockchain_facade = BlockchainFacade.get_instance()

    blockchain_facade.add_block_from_signed_change_request(
        signed_change_request=regular_node_declaration_signed_change_request,
        signing_key=primary_validator_key_pair.private,
        validate=False,
    )

    blockchain_facade.add_block_from_signed_change_request(
        signed_change_request=self_node_declaration_signed_change_request,
        signing_key=primary_validator_key_pair.private,
        validate=False,
    )

    blockchain_facade.add_block_from_signed_change_request(
        signed_change_request=confirmation_validator_declaration_signed_change_request,
        signing_key=primary_validator_key_pair.private,
        validate=False,
    )

    blockchain_facade.add_block_from_signed_change_request(
        signed_change_request=confirmation_validator_2_declaration_signed_change_request,
        signing_key=primary_validator_key_pair.private,
        validate=False,
    )

    blockchain_facade.add_block_from_signed_change_request(
        signed_change_request=make_pv_schedule_update_signed_change_request({
            '0': primary_validator_key_pair.public,
            '10000': confirmation_validator_key_pair.public,
            '20000': confirmation_validator_key_pair_2.public,
        }, primary_validator_key_pair),
        signing_key=primary_validator_key_pair.private,
        validate=False,
    )

    # TODO(dmu) MEDIUM: Add more blocks as new block types are developed


@pytest.fixture
def bloated_blockchain(
    rich_blockchain,
    primary_validator_key_pair,
    regular_node_declaration_signed_change_request,
    self_node_declaration_signed_change_request,
    test_server_address,
    primary_validator_node,
):
    blockchain_facade = BlockchainFacade.get_instance()

    for _ in range(24):
        node_key_pair = generate_key_pair()
        node = make_node(node_key_pair, [primary_validator_node.addresses[0], test_server_address])
        node_declaration_scr = make_node_declaration_signed_change_request(node, node_key_pair)
        blockchain_facade.add_block_from_signed_change_request(
            signed_change_request=node_declaration_scr,
            signing_key=primary_validator_key_pair.private,
            validate=False,
        )

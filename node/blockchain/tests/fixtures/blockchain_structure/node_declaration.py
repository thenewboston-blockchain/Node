import pytest

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import BlockMessage, NodeDeclarationSignedChangeRequest
from node.blockchain.tests.factories.signed_change_request.node_declaration import (
    make_node_declaration_signed_change_request
)
from node.blockchain.tests.factories.signed_change_request_message.node_declaration import (
    make_node_declaration_signed_change_request_message
)


@pytest.fixture
def node_declaration_signed_change_request_message(regular_node, db):
    return make_node_declaration_signed_change_request_message(regular_node)


@pytest.fixture
def regular_node_declaration_signed_change_request(regular_node, regular_node_key_pair, db):
    return make_node_declaration_signed_change_request(regular_node, regular_node_key_pair)


@pytest.fixture
def self_node_declaration_signed_change_request(self_node, self_node_key_pair, db):
    return make_node_declaration_signed_change_request(self_node, self_node_key_pair)


@pytest.fixture
def node_declaration_block_message(
    node_declaration_signed_change_request_message, regular_node_key_pair, base_blockchain, db
):
    request = NodeDeclarationSignedChangeRequest.create_from_signed_change_request_message(
        message=node_declaration_signed_change_request_message,
        signing_key=regular_node_key_pair.private,
    )
    return BlockMessage.create_from_signed_change_request(request, BlockchainFacade.get_instance())

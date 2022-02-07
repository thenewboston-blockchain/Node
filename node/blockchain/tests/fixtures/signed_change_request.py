import pytest

from node.blockchain.tests.factories.signed_change_request.node_declaration import (
    make_node_declaration_signed_change_request
)


@pytest.fixture
def regular_node_declaration_signed_change_request(regular_node, regular_node_key_pair, db):
    return make_node_declaration_signed_change_request(regular_node, regular_node_key_pair)


@pytest.fixture
def self_node_declaration_signed_change_request(self_node, self_node_key_pair, db):
    return make_node_declaration_signed_change_request(self_node, self_node_key_pair)

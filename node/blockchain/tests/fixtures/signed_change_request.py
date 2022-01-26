import pytest

from node.blockchain.tests.base import get_node_declaration_signed_change_request


@pytest.fixture
def regular_node_declaration_signed_change_request(regular_node, regular_node_key_pair):
    return get_node_declaration_signed_change_request(regular_node, regular_node_key_pair)


@pytest.fixture
def self_node_declaration_signed_change_request(self_node, self_node_key_pair):
    return get_node_declaration_signed_change_request(self_node, self_node_key_pair)

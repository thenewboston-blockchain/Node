import pytest

from node.blockchain.tests.factories.signed_change_request_message.node_declaration import (
    make_node_declaration_signed_change_request_message
)


@pytest.fixture
def node_declaration_signed_change_request_message(regular_node, db):
    return make_node_declaration_signed_change_request_message(regular_node)

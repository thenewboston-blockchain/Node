import pytest

from node.blockchain.inner_models import NodeDeclarationSignedChangeRequestMessage, SignedChangeRequest


def get_node_declaration_signed_change_request(node, node_key_pair):
    message = NodeDeclarationSignedChangeRequestMessage(
        node=node,
        account_lock=node.identifier,
    )

    signed_change_request = SignedChangeRequest.create_from_signed_change_request_message(
        message=message,
        signing_key=node_key_pair.private,
    )
    assert signed_change_request.message
    assert signed_change_request.signer
    assert signed_change_request.signature

    return signed_change_request


@pytest.fixture
def regular_node_declaration_signed_change_request(regular_node, regular_node_key_pair):
    return get_node_declaration_signed_change_request(regular_node, regular_node_key_pair)


@pytest.fixture
def self_node_declaration_signed_change_request(self_node, self_node_key_pair):
    return get_node_declaration_signed_change_request(self_node, self_node_key_pair)

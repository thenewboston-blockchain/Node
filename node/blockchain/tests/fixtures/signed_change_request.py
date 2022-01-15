import pytest

from node.blockchain.inner_models import NodeDeclarationSignedChangeRequestMessage, SignedChangeRequest


@pytest.fixture
def regular_node_declaration_signed_change_request(regular_node, regular_node_key_pair):
    message = NodeDeclarationSignedChangeRequestMessage(
        node=regular_node,
        account_lock=regular_node.identifier,
    )

    signed_change_request = SignedChangeRequest.create_from_signed_change_request_message(
        message=message,
        signing_key=regular_node_key_pair.private,
    )
    assert signed_change_request.message
    assert signed_change_request.signer
    assert signed_change_request.signature

    return signed_change_request

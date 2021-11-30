import pytest

from node.blockchain.inner_models import NodeDeclarationSignedChangeRequestMessage, SignedChangeRequest, BlockMessage
from node.core.utils.types import AccountLock


@pytest.fixture
def node_declaration_signed_change_request_message(regular_node):
    return NodeDeclarationSignedChangeRequestMessage(
        account_lock=AccountLock(regular_node.identifier),
        node=regular_node,
    )


@pytest.fixture
def genesis_block_message(node_declaration_signed_change_request_message,
                          regular_node_key_pair):
    request = SignedChangeRequest.create_from_signed_change_request_message(
        message=node_declaration_signed_change_request_message,
        signing_key=regular_node_key_pair.private,
    )
    return BlockMessage.create_from_signed_change_request(request)

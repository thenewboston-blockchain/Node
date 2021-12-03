import pytest

from node.blockchain.inner_models import NodeDeclarationSignedChangeRequestMessage
from node.core.utils.types import AccountLock


@pytest.fixture
def node_declaration_signed_change_request_message(regular_node):
    return NodeDeclarationSignedChangeRequestMessage(
        account_lock=AccountLock(regular_node.identifier),
        node=regular_node,
    )

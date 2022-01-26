from contextlib import contextmanager
from unittest.mock import patch

from node.blockchain.inner_models import Node, NodeDeclarationSignedChangeRequestMessage, SignedChangeRequest
from node.blockchain.types import KeyPair, NodeRole


@contextmanager
def as_role(node_role: NodeRole):
    with patch('node.blockchain.facade.BlockchainFacade.get_node_role', return_value=node_role):
        yield


def get_node_declaration_signed_change_request(node: Node, node_key_pair: KeyPair) -> SignedChangeRequest:
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

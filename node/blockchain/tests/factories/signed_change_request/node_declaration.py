from node.blockchain.inner_models import Node, NodeDeclarationSignedChangeRequest
from node.blockchain.types import KeyPair

from ..signed_change_request_message.node_declaration import make_node_declaration_signed_change_request_message


def make_node_declaration_signed_change_request(
    node: Node, node_key_pair: KeyPair
) -> NodeDeclarationSignedChangeRequest:
    signed_change_request = NodeDeclarationSignedChangeRequest.create_from_signed_change_request_message(
        message=make_node_declaration_signed_change_request_message(node),
        signing_key=node_key_pair.private,
    )
    assert signed_change_request.message
    assert signed_change_request.signer
    assert signed_change_request.signature

    return signed_change_request

from node.blockchain.inner_models import NodeDeclarationBlockMessage

from ..signed_change_request.node_declaration import make_node_declaration_signed_change_request


def make_node_declaration_block_message(node, node_key_pair, blockchain_facade) -> NodeDeclarationBlockMessage:
    request = make_node_declaration_signed_change_request(node, node_key_pair)
    return NodeDeclarationBlockMessage.create_from_signed_change_request(request, blockchain_facade)

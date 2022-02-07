from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import Node, NodeDeclarationSignedChangeRequestMessage


def make_node_declaration_signed_change_request_message(node: Node) -> NodeDeclarationSignedChangeRequestMessage:
    return NodeDeclarationSignedChangeRequestMessage(
        node=node,
        account_lock=BlockchainFacade.get_instance().get_account_lock(node.identifier),
    )

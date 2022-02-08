from node.blockchain.inner_models import Node


def make_node(node_key_pair, addresses):
    return Node(
        identifier=node_key_pair.public,
        addresses=addresses,
        fee=4,
    )

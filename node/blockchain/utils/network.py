import functools
from collections import defaultdict
from itertools import islice
from typing import Optional, Union

from node.blockchain.inner_models import Block, Node
from node.core.clients.node import NodeClient

from ..constants import LAST_BLOCK_ID

node_block_cache: dict[tuple, Optional[Block]] = {}


def get_nodes_for_syncing() -> list[Node]:
    # TODO(dmu) CRITICAL: Implement in https://thenewboston.atlassian.net/browse/BC-164
    #                     If local blockchain contains at least one node then use nodes from local blockchain
    #                     Otherwise try to get nodes from thenewboston.com end-point
    #                     Otherwise use nodes from JSON-file (stored during docker image build)
    #                     Otherwise return an empty list of nodes
    return []


def get_node_block(node: Node, block_number: Union[int, str]) -> Optional[Block]:
    node_identifier = node.identifier
    key = (node_identifier, block_number)
    if key in node_block_cache:
        block = node_block_cache[key]
    else:
        # We cache None with a meaning that a node does not have such a block
        node_block_cache[key] = block = NodeClient.get_instance().get_block(node, block_number)
        if block is not None and isinstance(block_number, str):
            node_block_cache[(node_identifier, block.get_block_number())] = block

    return block


def get_available_nodes(nodes: list[Node]):
    available_nodes = []
    for node in nodes:
        last_block = get_node_block(node, LAST_BLOCK_ID)
        if last_block is None:
            continue

        node.last_block = last_block
        available_nodes.append(node)

    return available_nodes


def clusterize_nodes(nodes):
    clusters = defaultdict(set)
    nodes = sorted(nodes, key=lambda _node: _node.last_block.get_block_number())
    for node_index, node in enumerate(nodes):
        last_block = node.last_block
        last_block_hash = last_block.make_hash()

        block_number = last_block.get_block_number()
        clusters[(block_number, last_block_hash)].add(node)

        for other_node in islice(nodes, node_index + 1, len(nodes)):
            block = get_node_block(other_node, block_number)
            if block is None:
                continue

            assert block.get_block_number() == block_number

            clusters[(block_number, block.make_hash())].add(other_node)

    return clusters


def get_best_cluster(clusters, majority_count):
    clusters = list(filter(lambda cluster: len(cluster) >= majority_count, clusters))
    if not clusters:
        return None

    return max(clusters, key=lambda cluster: len(cluster))


def clear_cache(func):

    @functools.wraps
    def wrapper(*args, **kwargs):
        node_block_cache.clear()
        rv = func(*args, **kwargs)
        node_block_cache.clear()
        return rv

    return wrapper


@clear_cache
def get_nodes_majority(nodes: list[Node]) -> Optional[list[Node]]:
    available_nodes = get_available_nodes(nodes)
    majority_count = len(available_nodes) // 2 + 1

    clusters = list(clusterize_nodes(available_nodes).values())
    return list(get_best_cluster(clusters, majority_count))

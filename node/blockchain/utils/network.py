from collections import defaultdict
from typing import Optional

from node.blockchain.inner_models.node import Node


def get_nodes_for_syncing() -> list[Node]:
    # TODO(dmu) CRITICAL: Implement in https://thenewboston.atlassian.net/browse/BC-164
    #                     If local blockchain contains at least one node then use nodes from local blockchain
    #                     Otherwise try to get nodes from thenewboston.com end-point
    #                     Otherwise use nodes from JSON-file (stored during docker image build)
    #                     Otherwise return an empty list of nodes
    return []


def get_node_last_block_number(node):
    raise NotImplementedError


def get_node_block_hash(node, block_number):
    raise NotImplementedError


def enrich_with_last_block_number(nodes):
    for node in nodes:
        node.last_block_number = get_node_last_block_number(node)


def get_nodes_majority(nodes: list[Node]) -> Optional[list[Node]]:
    # TODO(dmu) CRITICAL: Implement in https://thenewboston.atlassian.net/browse/BC-186
    clusters = defaultdict(set)
    enrich_with_last_block_number(nodes)
    # TODO(dmu) CRITICAL: Filter out offline nodes
    filtered_nodes = nodes
    sorted_nodes = sorted(filtered_nodes, key=lambda x: x.last_block_number)
    for node_index in range(len(sorted_nodes)):
        node = sorted_nodes[node_index]
        block_number = node.last_block_number

        block_hash = get_node_block_hash(node, block_number)
        clusters[(block_number, block_hash)].add(node)
        for other_node_index in range(node_index + 1, len(sorted_nodes)):
            other_node = sorted_nodes[other_node_index]
            block_hash = get_node_block_hash(other_node, block_number)
            clusters[(block_number, block_hash)].add(other_node)

    majority_count = len(nodes) // 2 + 1

    clusters_sorted = sorted(((key[0], key[1], len(value)) for key, value in clusters.items()), key=lambda x: x[2])
    for cluster_sorted in clusters_sorted:
        if cluster_sorted[2] < majority_count:
            continue

        return list(clusters[(cluster_sorted[0], cluster_sorted[1])])

    return None

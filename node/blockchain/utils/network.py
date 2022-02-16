import functools
import json
import logging
from collections import defaultdict
from itertools import islice
from typing import Optional, Union

from django.conf import settings

from node.blockchain.inner_models import Block, Node
from node.blockchain.models.node import Node as ORMNode
from node.core.clients.node import NodeClient
from node.core.utils.cryptography import get_node_identifier
from node.core.utils.misc import Wrapper

from ..constants import LAST_BLOCK_ID

logger = logging.getLogger(__name__)

node_block_cache: dict[tuple, Optional[Block]] = {}


def get_nodes_from_json_file(path) -> Optional[list[Node]]:
    try:
        with open(path) as fp:
            nodes_json = json.load(fp)
    except Exception:
        logger.warning('Unable to load nodes from %s', path, exc_info=True)
        return None

    nodes = []
    for node_json in nodes_json:
        try:
            node = Node.parse_obj(node_json)
        except Exception:
            logger.warning('Skipping invalid node: %s', node_json, exc_info=True)
            continue

        nodes.append(node)

    return nodes


def get_nodes_for_syncing() -> list[Node]:
    nodes = ORMNode.objects.exclude(_id=get_node_identifier()).all()
    if nodes:
        logger.debug('Got nodes from local blockchain')
        return [node.get_node() for node in nodes]
    logger.debug('No nodes in local blockchain')

    # TODO(dmu) HIGH: Otherwise try to get nodes from thenewboston.com end-point (use ThenewbostonComClient)
    #                 https://thenewboston.atlassian.net/browse/BC-185
    path = settings.NODE_LIST_JSON_PATH
    if path and (nodes := get_nodes_from_json_file(path)):
        logger.debug('Got nodes from %s', path)
        return nodes

    logger.debug('No nodes in node list json file (%s)', path)

    logger.debug('Nodes for syncing were not found')
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


def get_available_nodes(nodes: list[Node]) -> list[Wrapper]:
    available_nodes = []
    for node in nodes:
        last_block = get_node_block(node, LAST_BLOCK_ID)
        if last_block is None:
            continue

        available_nodes.append(Wrapper(node, last_block=last_block))

    return available_nodes


def clusterize_nodes(node_wrappers: list[Wrapper]):
    clusters = defaultdict(set)

    # Sort nodes, so we start from the longest blockchain
    node_wrappers = sorted(node_wrappers, key=lambda wrapper: wrapper.last_block.get_block_number())  # type: ignore
    for node_index, node_wrapper in enumerate(node_wrappers):
        last_block = node_wrapper.last_block  # type: ignore
        block_number = last_block.get_block_number()

        # Add node to cluster (either to existing or making new one)
        clusters[(block_number, last_block.make_hash())].add(node_wrapper)

        # See what hashes for the same block number do other nodes have
        for other_node_wrapper in islice(node_wrappers, node_index + 1, len(node_wrappers)):
            block = get_node_block(other_node_wrapper.body, block_number)
            if block is None:
                continue

            assert block.get_block_number() == block_number

            # Add node to cluster (either to existing or making new one)
            clusters[(block_number, block.make_hash())].add(other_node_wrapper)

    # Remove identical clusters (having exactly same nodes)
    reduced_clusters = set()
    for cluster in clusters.values():
        reduced_clusters.add(tuple(sorted(wrapper.body.identifier for wrapper in cluster)))

    # Produce clusters of nodes
    wrapper_by_identifier = {wrapper.body.identifier: wrapper for wrapper in node_wrappers}
    node_clusters = []
    for cluster in reduced_clusters:  # type: ignore
        block_number = min(
            wrapper_by_identifier[node_identifier].last_block.get_block_number()  # type: ignore
            for node_identifier in cluster
        )
        nodes = tuple(wrapper_by_identifier[node_identifier].body for node_identifier in cluster)
        node_clusters.append((block_number, nodes))

    return node_clusters


def get_best_cluster(clusters, majority_count):
    clusters = list(filter(lambda cluster: len(cluster[1]) >= majority_count, clusters))
    if not clusters:
        return None

    return max(clusters, key=lambda cluster: cluster[0])


def clear_cache(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        node_block_cache.clear()
        try:
            return func(*args, **kwargs)
        finally:
            node_block_cache.clear()

    return wrapper


@clear_cache
def get_nodes_majority(nodes: list[Node]) -> Optional[list[Node]]:
    available_nodes = get_available_nodes(nodes)
    if not available_nodes:
        return None

    majority_count = len(available_nodes) // 2 + 1
    clusters = clusterize_nodes(available_nodes)

    return get_best_cluster(clusters, majority_count) or None

from unittest.mock import MagicMock, patch

import pytest

from node.blockchain.inner_models import Node
from node.blockchain.models import Block
from node.blockchain.utils.network import clusterize_nodes, get_best_cluster, get_node_block, node_block_cache
from node.core.clients.node import NodeClient
from node.core.utils.misc import Wrapper


@pytest.mark.parametrize('block_number', (1, 'last'))
@pytest.mark.usefixtures('rich_blockchain', 'force_smart_mocked_node_client')
def test_get_node_block(test_server_address_regular_node, block_number):
    node = test_server_address_regular_node
    node_block_cache.clear()

    if block_number == 'last':
        orm_block = Block.objects.get_last_block()
    else:
        orm_block = Block.objects.get(_id=block_number)

    expected_block = orm_block.get_block()
    normalized_block_number = expected_block.get_block_number()

    block = get_node_block(node, block_number)
    assert block == expected_block

    expect_cache = {
        (node.identifier, block_number): block,
        (node.identifier, normalized_block_number): block,
    }
    assert node_block_cache == expect_cache

    with patch.object(NodeClient.get_instance(), 'get_block') as mock:
        block = get_node_block(node, block_number)

    mock.assert_not_called()
    assert block == expected_block
    assert node_block_cache == expect_cache


def test_clusterize_nodes_and_get_best_cluster():

    def make_block(block_number):
        return MagicMock(
            **{
                'get_block_number.return_value': block_number,
                'make_hash.return_value': str(block_number)
            }
        )

    node_clusters_1_2_3 = Wrapper(Node(identifier='0' * 64, addresses=['http://n0/'], fee=0), last_block=make_block(3))

    block_2 = make_block(2)
    node_1_clusters_1_2 = Wrapper(
        Node(identifier='1' * 64, addresses=['http://n1/'], fee=0),
        last_block=block_2,
    )

    node_2_clusters_1_2 = Wrapper(
        Node(identifier='2' * 64, addresses=['http://n2/'], fee=0),
        last_block=block_2,
    )

    node_3_clusters_1_2 = Wrapper(
        Node(identifier='3' * 64, addresses=['http://n3/'], fee=0),
        last_block=block_2,
    )

    node_clusters_1 = Wrapper(Node(identifier='4' * 64, addresses=['http://n4/'], fee=0), last_block=make_block(1))

    node_clusters_4 = Wrapper(
        Node(identifier='5' * 64, addresses=['http://n5/'], fee=0),
        last_block=MagicMock(**{
            'get_block_number.return_value': 3,
            'make_hash.return_value': 'another_3',
        })
    )

    cluster1 = [
        node_clusters_1.body, node_1_clusters_1_2.body, node_3_clusters_1_2.body, node_clusters_1_2_3.body,
        node_2_clusters_1_2.body
    ]
    cluster2 = [node_clusters_1_2_3.body, node_1_clusters_1_2.body, node_2_clusters_1_2.body, node_3_clusters_1_2.body]
    cluster3 = [node_clusters_1_2_3.body]
    cluster4 = [node_clusters_4.body]
    nodes = [
        # List is randomized on purpose: for better test coverage on random data
        node_1_clusters_1_2,
        node_clusters_1,
        node_3_clusters_1_2,
        node_clusters_1_2_3,
        node_2_clusters_1_2,
        node_clusters_4
    ]

    def get_block_node(node, block_number):
        if node.identifier == node_clusters_4.body.identifier:
            return MagicMock(
                **{
                    'get_block_number.return_value': block_number,
                    'make_hash.return_value': f'another_{block_number}',
                }
            )

        return make_block(block_number)

    with patch('node.blockchain.utils.network.get_node_block', new=get_block_node):
        clusters = clusterize_nodes(nodes)

    assert len(clusters) == 4

    def cluster_to_node_identifiers(cluster):
        return tuple(sorted(node.identifier for node in cluster))

    actual_clusters = tuple(sorted(cluster_to_node_identifiers(cluster[1]) for cluster in clusters))
    expected_clusters = tuple(
        sorted(cluster_to_node_identifiers(cluster) for cluster in (cluster1, cluster2, cluster3, cluster4))
    )
    assert expected_clusters == actual_clusters

    best_cluster = get_best_cluster(clusters, 4)
    # cluster2 is the best because it has the longest blockchain among clusters satisfying majority of nodes
    assert set(node.identifier for node in cluster2) == set(node.identifier for node in best_cluster)

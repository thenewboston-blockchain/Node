from unittest.mock import patch

import pytest

from node.blockchain.models import Block
from node.blockchain.utils.network import get_node_block, node_block_cache
from node.core.clients.node import NodeClient


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

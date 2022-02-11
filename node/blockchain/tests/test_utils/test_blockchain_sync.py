from unittest.mock import patch

import pytest

from node.blockchain.utils.blockchain_sync import sync_with_node


@pytest.mark.django_db
@pytest.mark.usefixtures('rich_blockchain', 'force_smart_mocked_node_client')
def test_sync_with_node_mocked(self_node_declared, test_server_address):
    with patch('node.blockchain.utils.blockchain_sync.sync_with_address', return_value=iter(((1, 1),))) as mock:
        next(sync_with_node(self_node_declared))

    mock.assert_called_once_with(test_server_address, to_block_number=2)

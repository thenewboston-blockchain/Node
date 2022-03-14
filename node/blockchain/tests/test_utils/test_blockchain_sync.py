from unittest.mock import patch

import pytest

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import NodeDeclarationBlock
from node.blockchain.models import Block as ORMBlock
from node.blockchain.tests.factories.block import make_block
from node.blockchain.tests.factories.block_message.node_declaration import make_node_declaration_block_message
from node.blockchain.utils.blockchain_sync import sync_with_address, sync_with_node


@pytest.mark.django_db
@pytest.mark.usefixtures('rich_blockchain', 'force_smart_mocked_node_client')
def test_sync_with_node_mocked(self_node_declared, test_server_address):
    with patch('node.blockchain.utils.blockchain_sync.sync_with_address', return_value=iter(((1, 1),))) as mock:
        next(sync_with_node(self_node_declared))

    mock.assert_called_once_with(test_server_address, to_block_number=5)


@pytest.mark.django_db
@pytest.mark.usefixtures('rich_blockchain', 'force_smart_mocked_node_client')
def test_sync_with_address(
    self_node_declared, test_server_address, primary_validator_key_pair, regular_node, regular_node_key_pair
):
    facade = BlockchainFacade.get_instance()
    start_block_number = facade.get_next_block_number()
    signing_key = primary_validator_key_pair.private

    expected_blocks = []

    def raw_block_generator(self, address, block_number_min, block_number_max):
        assert block_number_max - block_number_min + 1 == 5
        for expected_block_number in range(block_number_min, block_number_max + 1):
            block = make_block(
                make_node_declaration_block_message(regular_node, regular_node_key_pair, facade),
                signing_key,
                block_class=NodeDeclarationBlock
            )
            expected_blocks.append(block)
            assert block.get_block_number() == expected_block_number
            yield block.dict()

    with patch('node.core.clients.node.NodeClient.yield_blocks_dict', new=raw_block_generator):
        generator = sync_with_address(test_server_address, to_block_number=start_block_number + 4)
        assert next(generator) == (start_block_number, 0.2)
        assert next(generator) == (start_block_number + 1, 0.4)
        assert next(generator) == (start_block_number + 2, 0.6)
        assert next(generator) == (start_block_number + 3, 0.8)
        assert next(generator) == (start_block_number + 4, 1)
        with pytest.raises(StopIteration):
            next(generator)

    assert facade.get_next_block_number() == start_block_number + 5
    actual_blocks = ORMBlock.objects.filter(_id__in=range(start_block_number, start_block_number + 5)).order_by('_id')
    assert expected_blocks == [block.get_block() for block in actual_blocks]

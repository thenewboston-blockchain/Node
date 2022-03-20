from unittest.mock import patch

import pytest
from model_bakery import baker

from node.blockchain.models import Node
from node.blockchain.tasks.process_block_confirmations import get_next_block_confirmations
from node.blockchain.types import NodeRole


@pytest.mark.django_db
def test_get_next_block_confirmations():
    node0 = baker.make('blockchain.AccountState', _id='0' * 64, node={'fee': 1})
    node1 = baker.make('blockchain.AccountState', _id='1' * 64, node={'fee': 1})
    node2 = baker.make('blockchain.AccountState', _id='2' * 64, node={'fee': 1})
    baker.make('blockchain.AccountState', _id='3' * 64, node={'fee': 1})

    baker.make('blockchain.BlockConfirmation', number=4, signer=node0._id)
    bc2 = baker.make('blockchain.BlockConfirmation', number=3, signer=node0._id)
    bc3 = baker.make('blockchain.BlockConfirmation', number=3, signer=node1._id)

    return_value = Node.objects.filter(_id__in=(node0._id, node1._id, node2._id))
    with patch('node.blockchain.models.node.NodeQuerySet.filter_by_roles', return_value=return_value) as mock:
        assert set(get_next_block_confirmations(3)) == {bc2, bc3}

    mock.assert_called_once_with((NodeRole.CONFIRMATION_VALIDATOR,))

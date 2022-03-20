from unittest.mock import patch

import pytest
from model_bakery import baker

from node.blockchain.models import Node
from node.blockchain.tasks.process_block_confirmations import (
    get_consensus_block_hash_with_confirmations, get_next_block_confirmations
)
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


@pytest.mark.django_db
def test_get_consensus_block_hash_with_confirmations():
    bc0 = baker.make('blockchain.BlockConfirmation', number=3, signer='0' * 64, hash='a' * 128)
    bc1 = baker.make('blockchain.BlockConfirmation', number=3, signer='1' * 64, hash='a' * 128)
    bc2 = baker.make('blockchain.BlockConfirmation', number=3, signer='2' * 64, hash='b' * 128)

    confirmations = [bc0, bc1, bc2]
    result = get_consensus_block_hash_with_confirmations(confirmations, 2)
    assert result
    hash_, consensus_confirmations = result
    assert hash_ == bc0.hash
    assert consensus_confirmations == [bc0, bc1]

    result = get_consensus_block_hash_with_confirmations(confirmations, 3)
    assert result is None

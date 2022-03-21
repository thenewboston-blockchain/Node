from unittest.mock import patch

import pytest
from model_bakery import baker

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import BlockConfirmation as PydanticBlockConfirmation
from node.blockchain.models import BlockConfirmation, Node
from node.blockchain.tasks.process_block_confirmations import (
    get_consensus_block_hash_with_confirmations, get_next_block_confirmations, is_valid_consensus, process_next_block
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


@pytest.mark.parametrize('delta, is_valid', ((0, True), (1, False)))
@pytest.mark.django_db
def test_is_valid_consensus(delta, is_valid):
    block_number = BlockchainFacade.get_instance().get_next_block_number()
    bc0 = BlockConfirmation.objects.create_from_block_confirmation(
        PydanticBlockConfirmation.create(number=block_number + delta, hash_='a' * 64, signing_key='0' * 64)
    )
    bc1 = BlockConfirmation.objects.create_from_block_confirmation(
        PydanticBlockConfirmation.create(number=block_number + delta, hash_='a' * 64, signing_key='1' * 64)
    )
    bc2 = BlockConfirmation.objects.create_from_block_confirmation(
        PydanticBlockConfirmation.create(number=block_number + delta, hash_='a' * 64, signing_key='2' * 64)
    )

    confirmations = [bc0, bc1, bc2]
    assert is_valid_consensus(confirmations, 2) == is_valid


@pytest.mark.usefixtures('rich_blockchain')
@pytest.mark.django_db
def test_process_next_block_no_consensus():
    assert not process_next_block()


@pytest.mark.usefixtures('rich_blockchain')
@pytest.mark.django_db
def test_process_next_block_no_valid_consensus(confirmation_validator_key_pair, confirmation_validator_key_pair_2):
    facade = BlockchainFacade.get_instance()
    block_number = facade.get_next_block_number() + 1
    hash_ = 'a' * 64
    private_keys = {
        confirmation_validator_key_pair.public: confirmation_validator_key_pair.private,
        confirmation_validator_key_pair_2.public: confirmation_validator_key_pair_2.private,
    }
    identifiers = facade.get_confirmation_validator_identifiers()
    assert set(identifiers) == private_keys.keys()
    for identifier in identifiers:
        BlockConfirmation.objects.create_from_block_confirmation(
            PydanticBlockConfirmation.create(number=block_number, hash_=hash_, signing_key=private_keys[identifier])
        )

    assert not process_next_block()

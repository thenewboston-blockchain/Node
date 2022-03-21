from unittest.mock import patch

import pytest
from model_bakery import baker

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import BlockConfirmation as PydanticBlockConfirmation
from node.blockchain.models import BlockConfirmation, Node, PendingBlock
from node.blockchain.tasks.process_block_confirmations import (
    get_consensus_block_hash_with_confirmations, get_next_block_confirmations, is_valid_consensus,
    process_block_confirmations_task, process_next_block
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
    assert set(facade.get_confirmation_validator_identifiers()) == private_keys.keys()
    for private_key in private_keys.values():
        BlockConfirmation.objects.create_from_block_confirmation(
            PydanticBlockConfirmation.create(number=block_number, hash_=hash_, signing_key=private_key)
        )

    assert not process_next_block()


@pytest.mark.usefixtures('rich_blockchain', 'pending_block_confirmations')
@pytest.mark.django_db
def test_process_next_block_adds_new_block(pending_block):
    facade = BlockchainFacade.get_instance()
    block = pending_block.get_block()
    block_number = facade.get_next_block_number()

    assert facade.get_last_block() != block
    assert block.get_block_number() == block_number

    assert process_next_block()
    assert facade.get_next_block_number() == block_number + 1
    assert facade.get_last_block().get_block() == block


def test_process_block_confirmations_task():
    with patch(
        'node.blockchain.tasks.process_block_confirmations.process_next_block', side_effect=[True, True, False]
    ) as mock:
        process_block_confirmations_task()

    assert mock.call_count == 3


@pytest.mark.usefixtures('rich_blockchain', 'as_confirmation_validator')
def test_process_block_confirmations_integration(
    next_block, self_node_key_pair, confirmation_validator_key_pair, confirmation_validator_key_pair_2, api_client
):
    facade = BlockchainFacade.get_instance()
    block_number = facade.get_next_block_number()

    # Create pending block via API
    assert not PendingBlock.objects.exists()

    facade = BlockchainFacade.get_instance()
    block = next_block
    assert facade.get_primary_validator().identifier == block.signer

    payload = block.json()
    response = api_client.post('/api/blocks/', payload, content_type='application/json')
    assert response.status_code == 204

    pending_block = PendingBlock.objects.get_or_none(number=block.get_block_number(), hash=block.make_hash())
    assert pending_block
    assert pending_block.body == payload

    # TODO(dmu) CRITICAL: Remove artificial own confirmation
    #                     https://thenewboston.atlassian.net/browse/BC-263
    confirmation = PydanticBlockConfirmation.create_from_block(block, self_node_key_pair.private)
    BlockConfirmation.objects.create_from_block_confirmation(confirmation)

    # Create confirmations from other CVs
    for private_key in (confirmation_validator_key_pair.private, confirmation_validator_key_pair_2.private):
        confirmation = PydanticBlockConfirmation.create_from_block(block, private_key)
        payload = confirmation.json()
        response = api_client.post('/api/block-confirmations/', payload, content_type='application/json')
        assert response.status_code == 201

    # Assert that block was added to the blockchain
    assert facade.get_next_block_number() == block_number + 1
    assert facade.get_last_block().get_block() == block

import json
from unittest.mock import patch

import pytest
from django.db import connection

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import NodeDeclarationBlockMessage
from node.blockchain.models import Block, PendingBlock
from node.blockchain.tests.factories.block import make_block
from node.blockchain.tests.factories.block_message.node_declaration import make_node_declaration_block_message
from node.blockchain.types import Type


@pytest.mark.usefixtures('rich_blockchain')
def test_list_blocks_smoke(api_client):
    response = api_client.get('/api/blocks/')
    assert response.status_code == 200


@pytest.mark.usefixtures('rich_blockchain')
def test_list_blocks(api_client):
    response = api_client.get('/api/blocks/')
    assert response.status_code == 200
    response_json = response.json()
    results = response_json.get('results')
    assert isinstance(results, list)
    assert len(results) == 5

    for block_number in range(5):
        block = Block.objects.get(_id=block_number)
        response_block = results[block_number]
        expected_block = json.loads(block.body)
        assert response_block == expected_block


@pytest.mark.usefixtures('bloated_blockchain')
def test_list_blocks_range(api_client):
    response = api_client.get('/api/blocks/?block_number_min=3&block_number_max=6')
    assert response.status_code == 200
    response_json = response.json()
    results = response_json.get('results')
    assert isinstance(results, list)
    assert len(results) == 4

    for index, block_number in enumerate(range(3, 7)):
        block = Block.objects.get(_id=block_number)
        response_block = results[index]
        expected_block = json.loads(block.body)
        assert response_block == expected_block


@pytest.mark.usefixtures('rich_blockchain')
def test_blocks_pagination(api_client):
    response = api_client.get('/api/blocks/?limit=1')
    assert response.status_code == 200
    response_json = response.json()
    results = response_json.get('results')
    assert isinstance(results, list)
    assert len(results) == 1
    assert results[0] == json.loads(Block.objects.get(_id=0).body)

    response = api_client.get('/api/blocks/?limit=1&offset=1')
    assert response.status_code == 200
    response_json = response.json()
    results = response_json.get('results')
    assert isinstance(results, list)
    assert len(results) == 1
    assert results[0] == json.loads(Block.objects.get(_id=1).body)

    response = api_client.get('/api/blocks/?limit=1&offset=7')
    assert response.status_code == 200
    response_json = response.json()
    results = response_json.get('results')
    assert isinstance(results, list)
    assert len(results) == 0


@pytest.mark.usefixtures('rich_blockchain')
def test_list_blocks_blockchain_has_all_types():
    assert {block.get_block().message.type for block in Block.objects.order_by('_id')} == set(Type)


@pytest.mark.usefixtures('rich_blockchain')
def test_retrieve_block(api_client):
    response = api_client.get('/api/blocks/0/')
    assert response.status_code == 200
    assert response.json() == json.loads(Block.objects.get(_id=0).body)

    response = api_client.get('/api/blocks/1/')
    assert response.status_code == 200
    assert response.json() == json.loads(Block.objects.get(_id=1).body)


@pytest.mark.usefixtures('base_blockchain')
def test_create_pending_block(regular_node, regular_node_key_pair, primary_validator_key_pair, api_client):
    assert not PendingBlock.objects.exists()

    facade = BlockchainFacade.get_instance()
    block_message = make_node_declaration_block_message(regular_node, regular_node_key_pair, facade)

    assert facade.get_primary_validator().identifier == primary_validator_key_pair.public
    block = make_block(block_message, primary_validator_key_pair.private)

    payload = block.json()
    with patch('node.blockchain.views.block.start_process_pending_blocks_task') as mock:
        response = api_client.post('/api/blocks/', payload, content_type='application/json')

    assert response.status_code == 204
    mock.assert_called()
    pending_block = PendingBlock.objects.get_or_none(number=block.get_block_number(), hash=block.make_hash())
    assert pending_block
    assert pending_block.body == payload


@pytest.mark.usefixtures('rich_blockchain')
def test_try_to_create_outdated_block(regular_node, regular_node_key_pair, primary_validator_key_pair, api_client):
    assert not PendingBlock.objects.exists()

    facade = BlockchainFacade.get_instance()
    block_message = make_node_declaration_block_message(regular_node, regular_node_key_pair, facade)
    block_message_dict = block_message.dict()
    block_message_dict['number'] = facade.get_next_block_number() - 1
    block_message = NodeDeclarationBlockMessage.parse_obj(block_message_dict)

    assert facade.get_primary_validator().identifier == primary_validator_key_pair.public
    block = make_block(block_message, primary_validator_key_pair.private)

    payload = block.json()
    with patch('node.blockchain.views.block.start_process_pending_blocks_task') as mock:
        response = api_client.post('/api/blocks/', payload, content_type='application/json')

    assert response.status_code == 400
    assert response.json() == {'message': [{'code': 'invalid', 'message': 'Invalid number'}]}
    mock.assert_not_called()

    # This is because we have queried the database and nested transactions (save points) are not supported
    assert connection.needs_rollback
    connection.set_rollback(False)

    assert not PendingBlock.objects.exists()

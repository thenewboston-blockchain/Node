import json
from unittest.mock import patch

import pytest
from django.db import connection

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import NodeDeclarationBlockMessage
from node.blockchain.models import PendingBlock
from node.blockchain.tests.factories.block import make_block
from node.blockchain.tests.factories.block_message.node_declaration import make_node_declaration_block_message


@pytest.mark.usefixtures('base_blockchain')
def test_create_pending_block(regular_node, regular_node_key_pair, primary_validator_key_pair, api_client):
    assert not PendingBlock.objects.exists()

    facade = BlockchainFacade.get_instance()
    block_message = make_node_declaration_block_message(regular_node, regular_node_key_pair, facade)

    assert facade.get_primary_validator().identifier == primary_validator_key_pair.public
    block = make_block(block_message, primary_validator_key_pair.private)

    payload = block.json()
    with patch('node.blockchain.serializers.block.start_process_pending_blocks_task') as mock:
        response = api_client.post('/api/blocks/', payload, content_type='application/json')

    assert response.status_code == 204
    mock.assert_called()
    pending_block = PendingBlock.objects.get_or_none(number=block.get_block_number(), hash=block.make_hash())
    assert pending_block
    assert pending_block.body == payload


@pytest.mark.usefixtures('base_blockchain')
def test_create_future_block(regular_node, regular_node_key_pair, primary_validator_key_pair, api_client):
    assert not PendingBlock.objects.exists()

    facade = BlockchainFacade.get_instance()
    block_message = make_node_declaration_block_message(regular_node, regular_node_key_pair, facade)
    block_message_dict = block_message.dict()
    block_message_dict['number'] = facade.get_next_block_number() + 1
    block_message = NodeDeclarationBlockMessage.parse_obj(block_message_dict)

    assert facade.get_primary_validator().identifier == primary_validator_key_pair.public
    block = make_block(block_message, primary_validator_key_pair.private)

    payload = block.json()
    with patch('node.blockchain.serializers.block.start_process_pending_blocks_task') as mock:
        response = api_client.post('/api/blocks/', payload, content_type='application/json')

    assert response.status_code == 204
    mock.assert_not_called()
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
    with patch('node.blockchain.serializers.block.start_process_pending_blocks_task') as mock:
        response = api_client.post('/api/blocks/', payload, content_type='application/json')

    assert response.status_code == 400
    assert response.json() == [{'code': 'invalid', 'message': 'Invalid block number'}]
    mock.assert_not_called()

    # This is because we have queried the database and nested transactions (save points) are not supported
    assert connection.needs_rollback
    connection.set_rollback(False)

    assert not PendingBlock.objects.exists()


@pytest.mark.usefixtures('rich_blockchain')
def test_try_to_create_invalid_signature_block(
    regular_node, regular_node_key_pair, primary_validator_key_pair, api_client
):
    assert not PendingBlock.objects.exists()

    facade = BlockchainFacade.get_instance()
    block_message = make_node_declaration_block_message(regular_node, regular_node_key_pair, facade)

    assert facade.get_primary_validator().identifier == primary_validator_key_pair.public
    block = make_block(block_message, primary_validator_key_pair.private)

    payload_dict = json.loads(block.json())
    payload_dict['signature'] = '0' * 128
    payload = json.dumps(payload_dict)
    with patch('node.blockchain.serializers.block.start_process_pending_blocks_task') as mock:
        response = api_client.post('/api/blocks/', payload, content_type='application/json')

    assert response.status_code == 400
    assert response.json() == {'non_field_errors': [{'code': 'invalid', 'message': 'Invalid signature'}]}
    mock.assert_not_called()

    # This is because we have queried the database and nested transactions (save points) are not supported
    assert connection.needs_rollback
    connection.set_rollback(False)

    assert not PendingBlock.objects.exists()

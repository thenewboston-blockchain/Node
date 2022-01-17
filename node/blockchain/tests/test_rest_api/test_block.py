import json

import pytest

from node.blockchain.models import Block


@pytest.mark.usefixtures('rich_blockchain')
def test_list_blocks_smoke(api_client):
    response = api_client.get('/api/blocks/')
    assert response.status_code == 200


@pytest.mark.usefixtures('rich_blockchain')
def test_list_blocks(primary_validator_node, api_client):
    response = api_client.get('/api/blocks/')
    assert response.status_code == 200
    response_json = response.json()
    assert isinstance(response_json, list)
    assert len(response_json) == 2

    for block_number in range(2):
        block = Block.objects.get(_id=block_number)
        response_block = response_json[block_number]
        expected_block = json.loads(block.body)
        assert response_block == expected_block


@pytest.mark.usefixtures('rich_blockchain')
def test_blocks_pagination(primary_validator_node, api_client):
    response = api_client.get('/api/blocks/?limit=1')
    assert response.status_code == 200
    response_json = response.json()
    assert isinstance(response_json, list)
    assert len(response_json) == 1
    assert response_json[0] == json.loads(Block.objects.get(_id=0).body)

    response = api_client.get('/api/blocks/?limit=1&offset=1')
    assert response.status_code == 200
    response_json = response.json()
    assert isinstance(response_json, list)
    assert len(response_json) == 1
    assert response_json[0] == json.loads(Block.objects.get(_id=1).body)

    response = api_client.get('/api/blocks/?limit=1&offset=2')
    assert response.status_code == 200
    response_json = response.json()
    assert isinstance(response_json, list)
    assert len(response_json) == 0


@pytest.mark.usefixtures('rich_blockchain')
def test_retrieve_block(primary_validator_node, api_client):
    response = api_client.get('/api/blocks/0/')
    assert response.status_code == 200
    assert response.json() == json.loads(Block.objects.get(_id=0).body)

    response = api_client.get('/api/blocks/1/')
    assert response.status_code == 200
    assert response.json() == json.loads(Block.objects.get(_id=1).body)

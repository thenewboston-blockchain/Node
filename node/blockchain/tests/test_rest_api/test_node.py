import pytest


@pytest.mark.usefixtures('base_blockchain')
def test_list_nodes_smoke(api_client):
    response = api_client.get('/api/nodes/')
    assert response.status_code == 200


@pytest.mark.usefixtures('base_blockchain')
def test_list_nodes(primary_validator_node, api_client):
    response = api_client.get('/api/nodes/')
    assert response.status_code == 200
    assert response.json() == {
        'count':
            1,
        'results': [{
            'identifier': primary_validator_node.identifier,
            'addresses': primary_validator_node.addresses,
            'fee': primary_validator_node.fee
        }]
    }


# TODO(dmu) MEDIUM: Create `rich_blockchain` fixture containing more node and add more unittests with it


@pytest.mark.usefixtures('base_blockchain')
def test_retrieve_node(primary_validator_node, api_client):
    response = api_client.get(f'/api/nodes/{primary_validator_node.identifier}/')
    assert response.status_code == 200
    assert response.json() == {
        'identifier': primary_validator_node.identifier,
        'addresses': primary_validator_node.addresses,
        'fee': primary_validator_node.fee
    }

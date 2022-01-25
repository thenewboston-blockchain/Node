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


@pytest.mark.usefixtures('base_blockchain')
def test_retrieve_node(primary_validator_node, api_client):
    response = api_client.get(f'/api/nodes/{primary_validator_node.identifier}/')
    assert response.status_code == 200
    assert response.json() == {
        'identifier': primary_validator_node.identifier,
        'addresses': primary_validator_node.addresses,
        'fee': primary_validator_node.fee
    }


@pytest.mark.django_db
def test_retrieve_node_ruturns_404(api_client):
    response = api_client.get('/api/nodes/UNKNOWN_IDENTIFIER/')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not found.'}


@pytest.mark.usefixtures('rich_blockchain')
def test_retrieve_self_node(self_node, api_client):
    response = api_client.get('/api/nodes/self/')
    assert response.status_code == 200
    assert response.json() == {
        'identifier': self_node.identifier,
        'addresses': self_node.addresses,
        'fee': self_node.fee
    }

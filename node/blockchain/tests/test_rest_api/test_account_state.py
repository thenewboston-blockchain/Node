import pytest

from node.blockchain.models import AccountState


@pytest.mark.usefixtures('base_blockchain')
def test_retrieve_account_state(api_client, treasury_account_key_pair, treasury_amount):
    response = api_client.get(f'/api/account-states/{treasury_account_key_pair.public}/')
    assert response.status_code == 200
    assert response.json() == {
        '_id': treasury_account_key_pair.public,
        'balance': treasury_amount,
        'account_lock': treasury_account_key_pair.public,
        'node': None
    }


@pytest.mark.usefixtures('base_blockchain')
def test_retrieve_not_known_account_state(api_client):
    account_number = '0' * 64
    assert not AccountState.objects.filter(identifier=account_number).exists()
    response = api_client.get(f'/api/account-states/{account_number}/')
    assert response.status_code == 200
    assert response.json() == {'_id': account_number, 'balance': 0, 'account_lock': account_number, 'node': None}


@pytest.mark.django_db
def test_not_found(api_client):
    response = api_client.get('/api/account-states/INVALID_IDENTIFIER/')
    assert response.status_code == 404


@pytest.mark.usefixtures('base_blockchain')
def test_retrieve_when_node_is_not_empty(primary_validator_node, api_client):
    response = api_client.get(f'/api/account-states/{primary_validator_node.identifier}/')
    assert response.status_code == 200
    assert response.json() == {
        '_id': primary_validator_node.identifier,
        'balance': 0,
        'account_lock': primary_validator_node.identifier,
        'node': {
            'identifier': primary_validator_node.identifier,
            'addresses': primary_validator_node.addresses,
            'fee': primary_validator_node.fee
        }
    }

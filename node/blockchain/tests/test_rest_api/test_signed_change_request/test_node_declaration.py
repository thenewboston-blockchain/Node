import json
from unittest.mock import MagicMock, patch

import pytest

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import NodeDeclarationSignedChangeRequestMessage, SignedChangeRequest
from node.blockchain.models.node import Node
from node.blockchain.tests.base import as_role
from node.blockchain.tests.test_models.base import (
    CREATE, VALID, node_declaration_message_type_api_validation_parametrizer
)
from node.blockchain.types import NodeRole
from node.core.utils.collections import deep_update


@pytest.mark.usefixtures('base_blockchain', 'as_primary_validator')
def test_node_declaration_signed_change_request_as_primary_validator(api_client, regular_node, regular_node_key_pair):
    blockchain_facade = BlockchainFacade.get_instance()
    assert blockchain_facade.get_next_block_number() == 1
    assert blockchain_facade.get_node_by_identifier(regular_node.identifier) is None
    assert not Node.objects.filter(_id=regular_node.identifier).exists()

    message = NodeDeclarationSignedChangeRequestMessage(
        node=regular_node,
        account_lock=regular_node.identifier,
    )

    signed_change_request = SignedChangeRequest.create_from_signed_change_request_message(
        message=message,
        signing_key=regular_node_key_pair.private,
    )
    assert signed_change_request.message
    assert signed_change_request.signer
    assert signed_change_request.signature

    payload = signed_change_request.json()
    response = api_client.post('/api/signed-change-requests/', payload, content_type='application/json')
    assert response.status_code == 201
    assert response.json() == {
        'message': {
            'account_lock': '1c8e5f54a15b63a9f3d540ce505fd0799575ffeaac62ce625c917e6d915ea8bb',
            'node': {
                'addresses': ['http://not-existing-node-address-674898923.com:8555/'],
                'fee': 4,
                'identifier': '1c8e5f54a15b63a9f3d540ce505fd0799575ffeaac62ce625c917e6d915ea8bb'
            },
            'type': 1
        },
        'signature':
            'e6f950cce5fbe79ebc58dbd317ba7dec5baf6387bfeeb4656d73c8790d2564a4'
            '44f8c702b3e3ca931b5bb6e534781a135d5c17c4ff03886a80f32643dbd8fe0d',
        'signer': '1c8e5f54a15b63a9f3d540ce505fd0799575ffeaac62ce625c917e6d915ea8bb'
    }

    assert blockchain_facade.get_next_block_number() == 2
    node = blockchain_facade.get_node_by_identifier(regular_node.identifier)
    assert node
    assert node.identifier == regular_node.identifier
    assert node.fee == regular_node.fee
    assert node.addresses == regular_node.addresses


@pytest.mark.django_db
@node_declaration_message_type_api_validation_parametrizer
def test_type_validation_for_node_declaration(
    id_, regular_node, node, node_addresses, node_fee, account_lock, expected_response_body, api_client
):
    regular_node_dict = regular_node.dict()
    del regular_node_dict['identifier']
    payload = {
        'signer': '0' * 64,
        'signature': '0' * 128,
        'message': {
            'type':
                1,
            'account_lock':
                regular_node.identifier if account_lock is VALID else account_lock,
            'node':
                regular_node_dict if node is VALID else ({
                    'addresses': regular_node.addresses if node_addresses is VALID else node_addresses,
                    'fee': regular_node.fee if node_fee is VALID else node_fee,
                } if node is CREATE else node)
        }
    }
    response = api_client.post('/api/signed-change-requests/', payload)
    assert response.status_code == 400
    response_json = response.json()
    response_json.pop('non_field_errors', None)
    assert response_json == expected_response_body


@pytest.mark.parametrize('key', ('signer', 'signature', 'message'))
@pytest.mark.django_db
def test_checking_missed_keys(key, api_client, self_node_declaration_signed_change_request):
    # TODO(dmu) MEDIUM: Rename and extend test (parametrize) to test absence of `signer` and `signature`
    payload = self_node_declaration_signed_change_request.dict()
    del payload[key]
    response = api_client.post('/api/signed-change-requests/', json.dumps(payload), content_type='application/json')
    assert response.status_code == 400
    assert response.json() == {key: [{'code': 'required', 'message': 'This field is required.'}]}


@pytest.mark.usefixtures('base_blockchain', 'as_primary_validator')
def test_node_declaration_signed_change_request_with_invalid_account_lock(
    api_client, primary_validator_node, primary_validator_key_pair
):
    message = NodeDeclarationSignedChangeRequestMessage(
        node=primary_validator_node,
        account_lock='0' * 64,
    )

    signed_change_request = SignedChangeRequest.create_from_signed_change_request_message(
        message=message,
        signing_key=primary_validator_key_pair.private,
    )

    payload = signed_change_request.dict()

    response = api_client.post('/api/signed-change-requests/', payload)
    assert response.status_code == 400
    assert response.json() == {'non_field_errors': [{'code': 'invalid', 'message': 'Invalid account lock'}]}


@pytest.mark.django_db
@pytest.mark.parametrize('role', (NodeRole.PRIMARY_VALIDATOR, NodeRole.CONFIRMATION_VALIDATOR, NodeRole.REGULAR_NODE))
@pytest.mark.parametrize(
    'update_with', (
        ({
            'signature': '0' * 128
        }),
        ({
            'signer': '0' * 64
        }),
        ({
            'message': {
                'account_lock': '0' * 64
            }
        }),
    )
)
def test_signature_validation_for_node_declaration(
    role, update_with, api_client, primary_validator_node, primary_validator_key_pair
):
    message = NodeDeclarationSignedChangeRequestMessage(
        node=primary_validator_node,
        account_lock=primary_validator_node.identifier,
    )
    signed_change_request = SignedChangeRequest.create_from_signed_change_request_message(
        message=message,
        signing_key=primary_validator_key_pair.private,
    )
    payload = deep_update(signed_change_request.dict(), update_with)
    with as_role(role):
        response = api_client.post('/api/signed-change-requests/', payload)

    assert response.status_code == 400
    assert response.json() == {'non_field_errors': [{'code': 'invalid', 'message': 'Invalid signature'}]}


@pytest.mark.parametrize('role', (NodeRole.CONFIRMATION_VALIDATOR, NodeRole.REGULAR_NODE))
@pytest.mark.usefixtures('base_blockchain', 'mock_get_primary_validator')
def test_node_declaration_scr_as_other_roles(
    api_client, regular_node_declaration_signed_change_request, role, primary_validator_node
):
    signed_change_request = regular_node_declaration_signed_change_request

    payload = signed_change_request.json()

    response = MagicMock()
    response.status_code = 201
    response.content = payload.encode('utf-8')
    response.headers = {'content-type': 'application/json'}

    with as_role(role):
        with patch('node.core.clients.node.NodeClient.send_signed_change_request', return_value=response) as mock:
            response = api_client.post('/api/signed-change-requests/', payload, content_type='application/json')

    mock.assert_called_once_with(primary_validator_node, signed_change_request)

    assert response.status_code == 201
    assert response.json() == {
        'message': {
            'account_lock': '1c8e5f54a15b63a9f3d540ce505fd0799575ffeaac62ce625c917e6d915ea8bb',
            'node': {
                'addresses': ['http://not-existing-node-address-674898923.com:8555/'],
                'fee': 4,
            },
            'type': 1
        },
        'signature':
            'e6f950cce5fbe79ebc58dbd317ba7dec5baf6387bfeeb4656d73c8790d2564a4'
            '44f8c702b3e3ca931b5bb6e534781a135d5c17c4ff03886a80f32643dbd8fe0d',
        'signer': '1c8e5f54a15b63a9f3d540ce505fd0799575ffeaac62ce625c917e6d915ea8bb'
    }


@pytest.mark.parametrize(
    'update_with', (
        {
            'fee': 5
        },
        {
            'fee': 1
        },
        {
            'fee': 0
        },
        {
            'addresses': ['http://not-existing-address.com:5555/']
        },
        {
            'addresses': ['http://not-existing-address.com:5555/', 'http://not-existing-address.com:7777/']
        },
        {
            'fee': 5,
            'addresses': ['http://not-existing-address.com:5555/']
        },
    )
)
@pytest.mark.usefixtures('base_blockchain', 'as_primary_validator')
def test_update_node(update_with, api_client, primary_validator_node, primary_validator_key_pair):
    blockchain_facade = BlockchainFacade.get_instance()
    node = blockchain_facade.get_node_by_identifier(primary_validator_node.identifier)
    assert node.fee == 4
    assert node.addresses == ['http://not-existing-primary-validator-address-674898923.com:8555/']

    message = NodeDeclarationSignedChangeRequestMessage(
        node=deep_update(node.dict(), update_with),
        account_lock=primary_validator_node.identifier,
    )
    signed_change_request = SignedChangeRequest.create_from_signed_change_request_message(
        message=message,
        signing_key=primary_validator_key_pair.private,
    )
    payload = signed_change_request.json()
    response = api_client.post('/api/signed-change-requests/', payload, content_type='application/json')
    assert response.status_code == 201

    updated_node = blockchain_facade.get_node_by_identifier(primary_validator_node.identifier)
    assert node != updated_node
    assert response.json()['message']['node'] == updated_node.dict()

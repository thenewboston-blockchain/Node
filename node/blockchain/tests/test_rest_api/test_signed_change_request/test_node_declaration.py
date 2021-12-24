import pytest

from node.blockchain.inner_models import (
    GenesisSignedChangeRequestMessage, NodeDeclarationSignedChangeRequestMessage, SignedChangeRequest
)
from node.blockchain.tests.test_models.base import (
    CREATE, VALID, node_declaration_message_type_api_validation_parametrizer
)
from node.core.utils.collections import deep_update
from node.core.utils.types import AccountLock


@pytest.mark.django_db
@pytest.mark.usefixtures('base_blockchain')
def test_node_declaration_signed_change_request(api_client, regular_node, regular_node_key_pair):
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

    payload = signed_change_request.dict()
    response = api_client.post('/api/signed-change-request/', payload)
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


@pytest.mark.django_db
def test_restrict_genesis_signed_change_request(
    api_client, treasury_account_key_pair, treasury_amount, primary_validator_key_pair
):
    message = GenesisSignedChangeRequestMessage.create_from_treasury_account(
        account_lock=AccountLock(primary_validator_key_pair.public),
        treasury_account_number=treasury_account_key_pair.public,
        treasury_amount=treasury_amount
    )

    signed_change_request = SignedChangeRequest.create_from_signed_change_request_message(
        message=message,
        signing_key=primary_validator_key_pair.private,
    )

    payload = signed_change_request.dict()
    response = api_client.post('/api/signed-change-request/', payload)
    assert response.status_code == 400
    assert response.json() == {'message.type': ['Invalid value.']}


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
    response = api_client.post('/api/signed-change-request/', payload)
    assert response.status_code == 400
    assert response.json() == expected_response_body or response.json() == dict(
        expected_response_body,
        non_field_errors=['Invalid signature'],
    )


@pytest.mark.django_db
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

    response = api_client.post('/api/signed-change-request/', payload)
    assert response.status_code == 400
    assert response.json() == {'non_field_errors': ['Invalid account lock']}


@pytest.mark.django_db
@pytest.mark.parametrize(
    'update_with', (
        (dict(signature='0' * 128)),
        (dict(signer='0' * 64)),
        (dict(message=dict(account_lock=('0' * 64)))),
    )
)
def test_signature_validation_for_node_declaration(
    update_with, api_client, primary_validator_node, primary_validator_key_pair
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
    response = api_client.post('/api/signed-change-request/', payload)
    assert response.status_code == 400
    assert response.json() == {'non_field_errors': ['Invalid signature']}


@pytest.mark.skip('Not Implemented yet')
def test_confirmation_validator_signed_change_request():
    # TODO HIGH: Imlement similar test as "test_node_declaration_signed_change_request" for Confirmation Validator
    #            https://thenewboston.atlassian.net/browse/BC-188
    raise NotImplementedError


@pytest.mark.skip('Not Implemented yet')
def test_regular_node_signed_change_request():
    # TODO HIGH: Imlement similar test as "test_node_declaration_signed_change_request" for Confirmation Validator
    #            https://thenewboston.atlassian.net/browse/BC-188
    raise NotImplementedError

import pytest

from node.blockchain.inner_models import NodeDeclarationSignedChangeRequestMessage, SignedChangeRequest
from node.blockchain.tests.test_models.base import (
    CREATE, VALID, node_declaration_message_type_api_validation_parametrizer
)
from node.core.utils.collections import deep_update


@pytest.mark.django_db
def test_node_declaration_signed_change_request_can_be_sent_via_api(api_client, regular_node, regular_node_key_pair):
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
    # TODO(dmu) CRITICAL: Expect `assert response.status_code == 204` instead once `perform_create()` is implemented
    #                     https://thenewboston.atlassian.net/browse/BC-167
    with pytest.raises(NotImplementedError, match=f'"signer":"{regular_node.identifier}"'):
        api_client.post('/api/signed-change-request/', payload)


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
@pytest.mark.parametrize(
    'update_with', (
        (dict(signature='0' * 128)),
        (dict(signer='0' * 64)),
        (dict(message=dict(account_lock=('0' * 64)))),
    )
)
def test_signature_validation_for_node_declaration(update_with, api_client, regular_node, regular_node_key_pair):
    message = NodeDeclarationSignedChangeRequestMessage(
        node=regular_node,
        account_lock=regular_node.identifier,
    )
    signed_change_request = SignedChangeRequest.create_from_signed_change_request_message(
        message=message,
        signing_key=regular_node_key_pair.private,
    )
    payload = deep_update(signed_change_request.dict(), update_with)
    response = api_client.post('/api/signed-change-request/', payload)
    assert response.status_code == 400
    assert response.json() == {'non_field_errors': ['Invalid signature']}

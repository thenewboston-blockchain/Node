import pytest


def test_node_declaration_signed_change_request_can_be_sent_via_api(api_client, regular_node):
    payload = {
        # TODO(dmu) CRITICAL: Replace `signer`, `signature` and `account_lock` with valid values once
        #                     signature validation is implemented
        #                     https://thenewboston.atlassian.net/browse/BC-157
        'signer': '0' * 64,
        'signature': '0' * 128,
        'message': {
            'type': 1,
            'account_lock': regular_node.identifier,
            'node': regular_node.dict(),
        }
    }
    # TODO(dmu) CRITICAL: Expect `assert response.status_code == 204` instead once `perform_create()` is implemented
    #                     https://thenewboston.atlassian.net/browse/BC-167
    with pytest.raises(
        NotImplementedError, match='"identifier": "1c8e5f54a15b63a9f3d540ce505fd0799575ffeaac62ce625c917e6d915ea8bb"'
    ):
        api_client.post('/api/signed-change-request/', payload)

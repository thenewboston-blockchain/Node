from unittest.mock import MagicMock, call

import pytest
from requests.exceptions import HTTPError

from node.blockchain.facade import BlockchainFacade
from node.blockchain.models import Block, Node
from node.core.tests.base import make_node


def test_send_scr_to_address(
    primary_validator_node, regular_node_declaration_signed_change_request, mocked_node_client
):
    client = mocked_node_client

    address = primary_validator_node.addresses[0]
    scr = regular_node_declaration_signed_change_request

    rv = MagicMock()
    rv.status_code = 201
    client.requests_post.return_value = rv
    client.send_scr_to_address(address, scr)
    client.requests_post.assert_called_once_with(
        str(address) + 'api/signed-change-requests/',
        json=None,
        data=scr.json(),
        headers={'Content-Type': 'application/json'},
        timeout=2,
    )


@pytest.mark.django_db
@pytest.mark.usefixtures('base_blockchain')
def test_send_scr_to_address_integration(
    test_server_address, regular_node_declaration_signed_change_request, smart_mocked_node_client
):
    assert BlockchainFacade.get_next_block_number() == 1
    assert not Node.objects.filter(_id=regular_node_declaration_signed_change_request.signer).exists()

    client = smart_mocked_node_client
    scr = regular_node_declaration_signed_change_request
    response = client.send_scr_to_address(test_server_address, scr)
    assert response.status_code == 201

    assert BlockchainFacade.get_next_block_number() == 2
    assert Node.objects.filter(_id=regular_node_declaration_signed_change_request.signer).exists()


def test_send_scr_to_node(
    primary_validator_key_pair, primary_validator_node, regular_node_declaration_signed_change_request,
    mocked_node_client
):
    response1 = MagicMock()
    response1.status_code = 503
    response1.raise_for_status.side_effect = HTTPError
    response2 = MagicMock()
    response2.status_code = 201

    client = mocked_node_client
    client.requests_post.side_effect = [response1, response2]

    node = make_node(primary_validator_key_pair, [primary_validator_node.addresses[0], 'http://testserver/'])
    scr = regular_node_declaration_signed_change_request
    client.send_scr_to_node(node, scr)
    client.requests_post.assert_has_calls((
        call(
            str(primary_validator_node.addresses[0]) + 'api/signed-change-requests/',
            json=None,
            data=scr.json(),
            headers={'Content-Type': 'application/json'},
            timeout=2,
        ),
        call(
            'http://testserver/api/signed-change-requests/',
            json=None,
            data=scr.json(),
            headers={'Content-Type': 'application/json'},
            timeout=2,
        ),
    ))


@pytest.mark.django_db
@pytest.mark.usefixtures('rich_blockchain')
@pytest.mark.parametrize('block_identifier, block_number', (
    (0, 0),
    (1, 1),
    (2, 2),
    ('last', 2),
))
def test_get_block_raw(test_server_address, smart_mocked_node_client, block_identifier, block_number):
    block = smart_mocked_node_client.get_block_raw(test_server_address, block_identifier)
    expected_block = Block.objects.get(_id=block_number)
    assert block == expected_block.body


@pytest.mark.django_db
def test_get_block_raw_last_from_empty_blockchain(test_server_address, smart_mocked_node_client):
    block = smart_mocked_node_client.get_block_raw(test_server_address, 'last')
    assert block is None


# TODO(dmu) CRITICAL: Fix the unittest
@pytest.mark.skip('Failing')
@pytest.mark.parametrize(
    'offset, limit, expected_count', (
        (None, None, 2),
        (None, 1, 1),
        (1, None, 1),
        (2, None, 0),
        (2, 1, 0),
    )
)
@pytest.mark.usefixtures('rich_blockchain')
def test_list_nodes(offset, limit, expected_count, test_server_address, smart_mocked_node_client):
    client = smart_mocked_node_client

    response = client.list_nodes(test_server_address, offset, limit)
    assert response.status_code == 200
    message = response.json()
    assert len(message['results']) == expected_count

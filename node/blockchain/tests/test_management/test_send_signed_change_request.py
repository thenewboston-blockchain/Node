import json
from io import StringIO

import pytest
from django.core.management import call_command

from node.blockchain.tests.base import as_role
from node.blockchain.types import NodeRole


@as_role(NodeRole.PRIMARY_VALIDATOR)
@pytest.mark.usefixtures('rich_blockchain')
def test_node_declaration(test_server_address, force_smart_mocked_node_client, primary_validator_key_pair):
    out = StringIO()
    call_command(
        'send_signed_change_request',
        'NODE_DECLARATION',
        '--address=http://127.0.0.1:8000/',
        '--address=http://127.0.0.2:8000/',
        node_address=test_server_address,
        signing_key=primary_validator_key_pair.private,
        identifier=primary_validator_key_pair.public,
        fee=3,
        stdout=out
    )
    assert json.loads(out.getvalue().rstrip('\n')) == {
        'message': {
            'account_lock': 'b9dc49411424cce606d27eeaa8d74cb84826d8a1001d17603638b73bdc6077f1',
            'node': {
                'addresses': ['http://127.0.0.1:8000/', 'http://127.0.0.2:8000/'],
                'fee': 3,
                'identifier': primary_validator_key_pair.public
            },
            'type': 1
        },
        'signature':
            'f43d2e6e4edeba43fe4ea7e71c75140c985a649e6796ae81e64c0220c9f24a1a'
            '1312813b5410a1ec010e33b3f0a907db997b4c4a7556a0d9c0f3483b9595ca0a',
        'signer': primary_validator_key_pair.public
    }


@pytest.mark.usefixtures('rich_blockchain')
def test_node_declaration_when_signing_key_is_wrong(
    test_server_address, force_smart_mocked_node_client, regular_node_key_pair
):
    out = StringIO()
    with pytest.raises(SystemExit):
        call_command(
            'send_signed_change_request',
            'NODE_DECLARATION',
            node_address=test_server_address,
            signing_key='0' * 64,
            identifier=regular_node_key_pair.public,
            addresses=['http://127.0.0.1:8000/'],
            fee=3,
            stdout=out
        )
    assert out.getvalue().rstrip('\n') == 'Node address or signing key are wrong.'


@as_role(NodeRole.PRIMARY_VALIDATOR)
@pytest.mark.usefixtures('rich_blockchain')
def test_coin_transfer(
    test_server_address, force_smart_mocked_node_client, treasury_account_key_pair, regular_node_key_pair
):
    out = StringIO()
    payment_transaction = {
        'recipient': regular_node_key_pair.public,
        'is_fee': False,
        'amount': 100,
        'memo': 'message'
    }
    fee_transaction = {'recipient': regular_node_key_pair.public, 'is_fee': True, 'amount': 5, 'memo': 'fee'}
    call_command(
        'send_signed_change_request',
        'COIN_TRANSFER',
        f'--tx={json.dumps(payment_transaction)}',
        f'--tx={json.dumps(fee_transaction)}',
        node_address=test_server_address,
        signing_key=treasury_account_key_pair.private,
        stdout=out
    )
    assert json.loads(out.getvalue().rstrip('\n')) == {
        'message': {
            'account_lock': '4d3cf1d9e4547d324de2084b568f807ef12045075a7a01b8bec1e7f013fc3732',
            'txs': [{
                'amount': 100,
                'is_fee': False,
                'memo': 'message',
                'recipient': regular_node_key_pair.public
            }, {
                'amount': 5,
                'is_fee': True,
                'memo': 'fee',
                'recipient': regular_node_key_pair.public
            }],
            'type': 2
        },
        'signature':
            '3fef560daf38cedd90c12d7479930d007dd079140142ce6d671a2e06f8a2e0c6'
            'a9605266074794f4d1045527e236b66902ed935d2a2f3ab4d54296fe22004e02',
        'signer': treasury_account_key_pair.public
    }

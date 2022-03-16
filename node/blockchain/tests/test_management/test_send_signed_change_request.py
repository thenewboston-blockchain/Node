import json
from io import StringIO

import pytest
from django.core.management import call_command

from node.blockchain.facade import BlockchainFacade
from node.blockchain.tests.base import as_role
from node.blockchain.types import NodeRole


@as_role(NodeRole.PRIMARY_VALIDATOR)
@pytest.mark.usefixtures('rich_blockchain')
def test_node_declaration(test_server_address, force_smart_mocked_node_client, primary_validator_key_pair):
    out = StringIO()
    call_command(
        'add_signed_change_request',
        '1',
        test_server_address,
        primary_validator_key_pair.private,
        3,
        'http://127.0.0.1:8000/',
        'http://127.0.0.2:8000/',
        stdout=out
    )
    _, output = out.getvalue().split('Response (raw):')
    assert json.loads(output) == {
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


@as_role(NodeRole.PRIMARY_VALIDATOR)
@pytest.mark.usefixtures('rich_blockchain')
def test_coin_transfer(
    test_server_address, force_smart_mocked_node_client, treasury_account_key_pair, regular_node, self_node
):
    out = StringIO()

    payment_transaction = {'recipient': regular_node.identifier, 'is_fee': False, 'amount': 100, 'memo': 'payment'}
    fee_transaction = {'recipient': self_node.identifier, 'is_fee': True, 'amount': self_node.fee, 'memo': 'fee'}

    call_command(
        'add_signed_change_request',
        '2',
        test_server_address,
        treasury_account_key_pair.private,
        json.dumps(payment_transaction),
        json.dumps(fee_transaction),
        stdout=out
    )
    _, output = out.getvalue().split('Response (raw):')
    assert json.loads(output) == {
        'message': {
            'account_lock': '572795e9eb525f7c5ff601b001e8c13bac148b488fbe0142dfdaa6841148648d',
            'txs': [{
                'amount': 100,
                'is_fee': False,
                'memo': 'payment',
                'recipient': '1c8e5f54a15b63a9f3d540ce505fd0799575ffeaac62ce625c917e6d915ea8bb'
            }, {
                'amount': 4,
                'is_fee': True,
                'memo': 'fee',
                'recipient': self_node.identifier
            }],
            'type': 2
        },
        'signature':
            '07f11055cba3d968123d2312e7d46cf95ad18be057b5ba0c1cb3c72670e5bee5'
            '70a7fbbb2f33ae4888a314d05142353d3472cf51ba5726aa12be01655bfbc906',
        'signer': '4d3cf1d9e4547d324de2084b568f807ef12045075a7a01b8bec1e7f013fc3732'
    }


@as_role(NodeRole.PRIMARY_VALIDATOR)
@pytest.mark.usefixtures('rich_blockchain')
def test_pv_schedule_update(
    test_server_address, force_smart_mocked_node_client, primary_validator_key_pair, self_node_key_pair
):
    out = StringIO()
    blockchain_facade = BlockchainFacade.get_instance()

    assert blockchain_facade.get_next_block_number() == 7

    schedule = {
        '7': primary_validator_key_pair.public,
    }
    call_command(
        'add_signed_change_request', '3', 'local', self_node_key_pair.private, json.dumps(schedule), stdout=out
    )
    assert 'Block added to local blockchain' in out.getvalue()

    block = blockchain_facade.get_last_block().get_block()
    assert block.message.update.schedule == schedule

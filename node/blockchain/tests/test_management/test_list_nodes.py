import json
from io import StringIO

import pytest
from django.core.management import call_command

from node.core.utils.cryptography import get_node_identifier


@pytest.mark.usefixtures('rich_blockchain')
def test_list_nodes(test_server_address, force_smart_mocked_node_client):
    out = StringIO()
    call_command('list_nodes', test_server_address, stdout=out)
    assert json.loads(out.getvalue().rstrip('\n')) == [{
        'addresses': ['http://not-existing-node-address-674898923.com:8555/'],
        'fee': 4,
        'identifier': '1c8e5f54a15b63a9f3d540ce505fd0799575ffeaac62ce625c917e6d915ea8bb'
    }, {
        'addresses': ['http://not-existing-self-address-674898923.com:8555/'],
        'fee': 4,
        'identifier': get_node_identifier()
    }, {
        'addresses': ['http://not-existing-primary-validator-address-674898923.com:8555/'],
        'fee': 4,
        'identifier': 'b9dc49411424cce606d27eeaa8d74cb84826d8a1001d17603638b73bdc6077f1'
    }]


@pytest.mark.django_db
def test_list_nodes_when_no_nodes(test_server_address, force_smart_mocked_node_client):
    out = StringIO()
    call_command('list_nodes', test_server_address, stdout=out)
    assert json.loads(out.getvalue().rstrip('\n')) == []

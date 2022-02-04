import json
from tempfile import NamedTemporaryFile

import pytest

from node.core.tests.base import make_node


@pytest.fixture
def regular_node(regular_node_key_pair):
    return make_node(regular_node_key_pair, ['http://not-existing-node-address-674898923.com:8555/'])


@pytest.fixture
def test_server_address_regular_node(regular_node_key_pair, test_server_address):
    return make_node(regular_node_key_pair, [test_server_address])


@pytest.fixture
def primary_validator_node(primary_validator_key_pair):
    return make_node(primary_validator_key_pair, ['http://not-existing-primary-validator-address-674898923.com:8555/'])


@pytest.fixture
def self_node(self_node_key_pair):
    return make_node(self_node_key_pair, ['http://not-existing-self-address-674898923.com:8555/'])


@pytest.fixture
def node_list_json_file_content():
    return [
        {
            'identifier': '4abe785508b4ae95c45930b64b6f3d1cc26a473e515fb68427089b524cbd0fd8',
            'addresses': ['http://34.221.75.138:8555/'],
            'fee': 4
        },
        {
            'identifier': '4abe7800000000000000000000000d1cc26a473e515fb68427089b524cbd0fd8',
            'addresses': ['http://34.112.57.249:8555/'],
            'fee': 4
        },
    ]


@pytest.fixture
def node_list_json_file(node_list_json_file_content):
    with NamedTemporaryFile('wt') as fp:
        json.dump(node_list_json_file_content, fp, separators=(',', ':'))
        fp.flush()
        yield fp

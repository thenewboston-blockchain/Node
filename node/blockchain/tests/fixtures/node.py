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

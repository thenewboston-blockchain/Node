import pytest

from node.blockchain.inner_models import Node


@pytest.fixture
def regular_node(regular_node_key_pair):
    return Node(
        identifier=regular_node_key_pair.public,
        addresses=['http://not-existing-node-address-674898923.com:8555/'],
        fee=4,
    )

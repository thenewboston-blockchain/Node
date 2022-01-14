import pytest

from node.blockchain.tests.base import as_role
from node.blockchain.types import NodeRole


@pytest.fixture
def as_primary_validator():
    with as_role(NodeRole.PRIMARY_VALIDATOR):
        yield

import pytest

from node.blockchain.facade import BlockchainFacade
from node.blockchain.models import Node as ORMNode
from node.blockchain.models import Schedule
from node.blockchain.types import NodeRole
from node.core.utils.cryptography import get_node_identifier


@pytest.mark.django_db
@pytest.mark.usefixtures('base_blockchain')
def test_get_node_role_as_not_declared():
    assert not ORMNode.objects.filter(_id=get_node_identifier()).exists()
    assert BlockchainFacade.get_instance().get_node_role() is None


@pytest.mark.django_db
@pytest.mark.usefixtures('base_blockchain', 'as_primary_validator')
def test_get_node_role_as_primary_validator():
    assert BlockchainFacade.get_instance().get_node_role() == NodeRole.PRIMARY_VALIDATOR


@pytest.mark.django_db
@pytest.mark.usefixtures('base_blockchain', 'as_confirmation_validator')
def test_get_node_role_as_confirmation_validator():
    assert BlockchainFacade.get_instance().get_node_role() == NodeRole.CONFIRMATION_VALIDATOR


@pytest.mark.django_db
@pytest.mark.usefixtures('base_blockchain', 'as_regular_node')
def test_get_node_role_as_regular_node():
    assert BlockchainFacade.get_instance().get_node_role() == NodeRole.REGULAR_NODE


@pytest.mark.django_db
@pytest.mark.usefixtures('rich_blockchain')
def test_get_node_role_used_to_be_primary_validator(primary_validator_key_pair):
    facade = BlockchainFacade.get_instance()
    node_identifier = get_node_identifier()
    Schedule.objects.filter(node_identifier=node_identifier).delete()

    next_block_number = facade.get_next_block_number()
    block_number = next_block_number - 1
    assert block_number >= 0
    Schedule.objects.create(_id=block_number, node_identifier=node_identifier)
    Schedule.objects.create(_id=next_block_number, node_identifier=primary_validator_key_pair.public)
    assert facade.get_node_role() == NodeRole.REGULAR_NODE

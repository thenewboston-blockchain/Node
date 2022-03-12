import pytest

from node.blockchain.facade import BlockchainFacade
from node.blockchain.models import Node as ORMNode
from node.blockchain.types import NodeRole
from node.core.utils.cryptography import get_node_identifier


@pytest.mark.usefixtures('base_blockchain')
def test_get_node_role_as_not_declared():
    blockchain_facade = BlockchainFacade.get_instance()
    assert blockchain_facade.get_node_by_identifier(get_node_identifier()) is None
    assert blockchain_facade.get_node_role() is None
    assert not ORMNode.objects.filter(identifier=get_node_identifier()).exists()


@pytest.mark.usefixtures('base_blockchain', 'as_primary_validator')
def test_get_node_role_as_primary_validator():
    assert BlockchainFacade.get_instance().get_node_role() == NodeRole.PRIMARY_VALIDATOR


@pytest.mark.usefixtures('base_blockchain', 'as_confirmation_validator')
def test_get_node_role_as_confirmation_validator():
    assert BlockchainFacade.get_instance().get_node_role() == NodeRole.CONFIRMATION_VALIDATOR


@pytest.mark.usefixtures('base_blockchain', 'as_regular_node')
def test_get_node_role_as_regular_node():
    assert BlockchainFacade.get_instance().get_node_role() == NodeRole.REGULAR_NODE


@pytest.mark.skip('Need to fix database error')
@pytest.mark.django_db
@pytest.mark.usefixtures('rich_blockchain')
def test_get_node_role_used_to_be_primary_validator(primary_validator_node):
    facade = BlockchainFacade.get_instance()
    node_identifier = get_node_identifier()
    ORMNode.objects.filter(identifier=node_identifier).delete()

    next_block_number = facade.get_next_block_number()
    block_number = next_block_number - 1
    assert block_number >= 0
    ORMNode.objects.create(identifier=node_identifier, block_number=block_number)
    ORMNode.objects.create(identifier=primary_validator_node.identifier, block_number=next_block_number)
    assert facade.get_node_role() == NodeRole.REGULAR_NODE

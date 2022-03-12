import pytest

from node.blockchain.facade import BlockchainFacade
from node.blockchain.models import Node


@pytest.mark.django_db
def test_get_primary_validator_empty_schedule():
    assert Node.objects.exclude(block_number__isnull=True).exists() is False
    assert BlockchainFacade.get_instance().get_primary_validator() is None


@pytest.mark.usefixtures('base_blockchain')
def test_get_primary_validator_basic(primary_validator_node):
    assert Node.objects.count() == 1
    node = Node.objects.get()
    assert node.block_number == 0
    assert node.identifier == primary_validator_node.identifier
    facade = BlockchainFacade.get_instance()
    assert facade.get_next_block_number() == 1
    assert facade.get_primary_validator() == primary_validator_node


@pytest.mark.usefixtures('base_blockchain')
def test_get_primary_validator_exactly_next_block(primary_validator_node, regular_node):
    assert Node.objects.count() == 1
    node = Node.objects.get()
    assert node.block_number == 0
    assert node.identifier == primary_validator_node.identifier
    facade = BlockchainFacade.get_instance()
    assert facade.get_next_block_number() == 1

    Node.objects.create(**regular_node.dict(), block_number=1)
    assert facade.get_primary_validator() == regular_node


@pytest.mark.usefixtures('base_blockchain')
def test_get_primary_validator_with_queue(primary_validator_node, regular_node):
    assert Node.objects.count() == 1
    node = Node.objects.get()
    assert node.block_number == 0
    assert node.identifier == primary_validator_node.identifier
    facade = BlockchainFacade.get_instance()
    assert facade.get_next_block_number() == 1

    Node.objects.create(**regular_node.dict(), block_number=2)
    assert facade.get_primary_validator() == primary_validator_node

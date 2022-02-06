import pytest

from node.blockchain.facade import BlockchainFacade
from node.blockchain.models import AccountState, Schedule


@pytest.mark.django_db
def test_get_primary_validator_empty_schedule():
    assert not Schedule.objects.exists()
    assert BlockchainFacade.get_instance().get_primary_validator() is None


@pytest.mark.usefixtures('base_blockchain')
def test_get_primary_validator_basic(primary_validator_node):
    assert Schedule.objects.all().count() == 1
    schedule = Schedule.objects.get_or_none()
    assert schedule
    assert schedule._id == 0
    assert schedule.node_identifier == primary_validator_node.identifier
    facade = BlockchainFacade.get_instance()
    assert facade.get_next_block_number() == 1
    assert facade.get_primary_validator() == primary_validator_node


@pytest.mark.usefixtures('base_blockchain')
def test_get_primary_validator_exactly_next_block(primary_validator_node, regular_node):
    assert Schedule.objects.all().count() == 1
    schedule = Schedule.objects.get_or_none()
    assert schedule
    assert schedule._id == 0
    assert schedule.node_identifier == primary_validator_node.identifier
    facade = BlockchainFacade.get_instance()
    assert facade.get_next_block_number() == 1

    Schedule.objects.create(_id=1, node_identifier=regular_node.identifier)
    AccountState.objects.create(_id=regular_node.identifier, node=regular_node.dict())
    assert facade.get_primary_validator() == regular_node


@pytest.mark.usefixtures('base_blockchain')
def test_get_primary_validator_with_queue(primary_validator_node, regular_node):
    assert Schedule.objects.all().count() == 1
    schedule = Schedule.objects.get_or_none()
    assert schedule
    assert schedule._id == 0
    assert schedule.node_identifier == primary_validator_node.identifier
    facade = BlockchainFacade.get_instance()
    assert facade.get_next_block_number() == 1

    Schedule.objects.create(_id=2, node_identifier=regular_node.identifier)
    AccountState.objects.create(_id=regular_node.identifier, node=regular_node.dict())
    assert facade.get_primary_validator() == primary_validator_node

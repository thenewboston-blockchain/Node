import pytest

from node.blockchain.facade import BlockchainFacade
from node.blockchain.models import Node as ORMNode
from node.blockchain.types import AccountNumber
from node.core.utils.types import non_negative_intstr

SCHEDULE_0 = {
    '0': '0' * 64,
    '100': '1' * 64,
    '200': '2' * 64,
}

SCHEDULE_EMPTY: dict[non_negative_intstr, AccountNumber] = {}

SCHEDULE_0_WITH_UPDATED_NODE_IDENTIFIERS = {
    '0': '7' * 64,
    '100': '8' * 64,
    '200': '9' * 64,
}

SCHEDULE_0_WITH_PARTIALLY_UPDATED_NODE_IDENTIFIERS = {
    '0': '0' * 64,
    '100': '8' * 64,
    '200': '2' * 64,
}

SCHEDULE_0_SMALL = {
    '0': '0' * 64,
}

SCHEDULE_100 = {
    '100': '1' * 64,
    '200': '2' * 64,
    '300': '3' * 64,
}

SCHEDULE_130 = {
    '130': '1' * 64,
    '200': '2' * 64,
    '300': '3' * 64,
}

SCHEDULE_500 = {
    '500': '5' * 64,
    '600': '6' * 64,
    '700': '7' * 64,
}


@pytest.mark.django_db
@pytest.mark.parametrize(
    'first_schedule, second_schedule', (
        (SCHEDULE_0, SCHEDULE_0),
        (SCHEDULE_0, SCHEDULE_EMPTY),
        (SCHEDULE_0, SCHEDULE_0_SMALL),
        (SCHEDULE_0, SCHEDULE_0_WITH_UPDATED_NODE_IDENTIFIERS),
        (SCHEDULE_0, SCHEDULE_0_WITH_PARTIALLY_UPDATED_NODE_IDENTIFIERS),
        (SCHEDULE_0, SCHEDULE_100),
        (SCHEDULE_100, SCHEDULE_130),
        (SCHEDULE_0, SCHEDULE_500),
        (SCHEDULE_130, SCHEDULE_100),
        (SCHEDULE_500, SCHEDULE_0),
        (SCHEDULE_100, SCHEDULE_0),
    )
)
def test_add_delete_update(first_schedule, second_schedule):
    blockchain_facade = BlockchainFacade.get_instance()
    assert ORMNode.objects.exclude(block_number__isnull=True).count() == 0

    for schedule in [first_schedule, second_schedule]:
        blockchain_facade.update_write_through_cache_schedule(schedule)

        assert ORMNode.objects.exclude(block_number__isnull=True).count() == len(schedule)
        assert ORMNode.objects.filter(block_number__in=schedule.keys()).count() == len(schedule)
        assert ORMNode.objects.filter(identifier__in=schedule.values()).count() == len(schedule)

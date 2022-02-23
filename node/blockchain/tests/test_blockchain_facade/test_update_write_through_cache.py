import pytest

from node.blockchain.facade import BlockchainFacade
from node.blockchain.models import Schedule
from node.blockchain.types import AccountNumber
from node.core.utils.types import intstr

SCHEDULE_0 = {
    '0': '0' * 64,
    '100': '1' * 64,
    '200': '2' * 64,
}

SCHEDULE_EMPTY: dict[intstr, AccountNumber] = {}

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
    assert Schedule.objects.count() == 0

    for schedule in [first_schedule, second_schedule]:
        blockchain_facade.update_write_through_cache_schedule(schedule)

        assert Schedule.objects.count() == len(schedule)
        assert Schedule.objects.filter(_id__in=schedule.keys()).count() == len(schedule)
        assert Schedule.objects.filter(node_identifier__in=schedule.values()).count() == len(schedule)

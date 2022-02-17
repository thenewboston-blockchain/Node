import pytest

from node.blockchain.tests.factories.signed_change_request_message.pv_schedule_update import (
    make_pv_schedule_update_signed_change_request_message
)


@pytest.fixture
def pv_schedule_update_signed_change_request_message(primary_validator_node, db):
    return make_pv_schedule_update_signed_change_request_message(primary_validator_node)

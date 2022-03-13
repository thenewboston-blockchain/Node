import pytest

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import BlockMessage, PVScheduleUpdateSignedChangeRequest
from node.blockchain.tests.factories.signed_change_request_message.pv_schedule_update import (
    make_pv_schedule_update_signed_change_request_message
)


@pytest.fixture
def pv_schedule_update_signed_change_request_message(primary_validator_node, db):
    return make_pv_schedule_update_signed_change_request_message({'1': primary_validator_node.identifier},
                                                                 primary_validator_node.identifier)


@pytest.fixture
def pv_schedule_update_signed_change_request(
    pv_schedule_update_signed_change_request_message, primary_validator_key_pair
):
    return PVScheduleUpdateSignedChangeRequest.create_from_signed_change_request_message(
        message=pv_schedule_update_signed_change_request_message,
        signing_key=primary_validator_key_pair.private,
    )


@pytest.fixture
def pv_schedule_update_block_message(pv_schedule_update_signed_change_request, base_blockchain, db):
    return BlockMessage.create_from_signed_change_request(
        pv_schedule_update_signed_change_request, BlockchainFacade.get_instance()
    )

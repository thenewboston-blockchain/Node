import pytest

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import PVScheduleUpdateBlockMessage


@pytest.mark.usefixtures('base_blockchain')
def test_make_block_message_update(pv_schedule_update_signed_change_request, primary_validator_node):
    request = pv_schedule_update_signed_change_request
    block_message_update = PVScheduleUpdateBlockMessage.make_block_message_update(
        request, BlockchainFacade.get_instance()
    )

    assert block_message_update.accounts is None

    schedule = block_message_update.schedule
    assert schedule == {'1': primary_validator_node.identifier}

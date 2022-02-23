import re
from datetime import datetime

import pytest
from pydantic import ValidationError

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import (
    BlockMessage, BlockMessageUpdate, PVScheduleUpdateBlockMessage, PVScheduleUpdateSignedChangeRequest
)
from node.blockchain.types import Type


@pytest.mark.django_db
@pytest.mark.usefixtures('base_blockchain')
def test_create_from_signed_change_request(
    pv_schedule_update_signed_change_request_message, primary_validator_key_pair
):
    request = PVScheduleUpdateSignedChangeRequest.create_from_signed_change_request_message(
        message=pv_schedule_update_signed_change_request_message,
        signing_key=primary_validator_key_pair.private,
    )
    blockchain_facade = BlockchainFacade.get_instance()
    expected_block_number = blockchain_facade.get_next_block_number()
    expected_identifier = blockchain_facade.get_next_block_identifier()

    message = BlockMessage.create_from_signed_change_request(request, blockchain_facade)
    assert message.number == expected_block_number
    assert message.identifier == expected_identifier
    assert message.type == Type.PV_SCHEDULE_UPDATE
    assert isinstance(message.timestamp, datetime)
    assert message.timestamp.tzinfo is None

    update = message.update
    assert update.schedule == {'1': primary_validator_key_pair.public}
    assert update.accounts is None


def test_serialize_deserialize_works(pv_schedule_update_block_message):
    serialized = pv_schedule_update_block_message.json()
    deserialized = BlockMessage.parse_raw(serialized)
    assert deserialized.type == pv_schedule_update_block_message.type
    assert deserialized.number == pv_schedule_update_block_message.number
    assert deserialized.identifier == pv_schedule_update_block_message.identifier
    assert deserialized.timestamp == pv_schedule_update_block_message.timestamp
    assert deserialized.request.signer == pv_schedule_update_block_message.request.signer
    assert deserialized.request.signature == pv_schedule_update_block_message.request.signature
    assert deserialized.request.message == pv_schedule_update_block_message.request.message
    assert deserialized.request == pv_schedule_update_block_message.request
    assert deserialized.update == pv_schedule_update_block_message.update
    assert deserialized == pv_schedule_update_block_message

    serialized2 = deserialized.json()
    assert serialized == serialized2


def test_block_identifier_is_mandatory(pv_schedule_update_signed_change_request, primary_validator_key_pair):
    PVScheduleUpdateBlockMessage(
        number=1,
        identifier='0' * 64,
        timestamp=datetime.utcnow(),
        request=pv_schedule_update_signed_change_request,
        update=BlockMessageUpdate(schedule={'1': primary_validator_key_pair.public}),
    )

    with pytest.raises(ValidationError) as exc_info:
        PVScheduleUpdateBlockMessage(
            number=1,
            identifier=None,
            timestamp=datetime.utcnow(),
            request=pv_schedule_update_signed_change_request,
            update=BlockMessageUpdate(schedule={'1': primary_validator_key_pair.public}),
        )

    assert re.search(r'identifier.*none is not an allowed value', str(exc_info.value), flags=re.DOTALL)

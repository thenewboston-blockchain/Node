import json
import re

import pytest
from pydantic import ValidationError as PydanticValidationError

from node.blockchain.inner_models import SignedChangeRequest
from node.blockchain.inner_models.signed_change_request import PVScheduleUpdateSignedChangeRequest
from node.blockchain.tests.test_models.base import (
    VALID, pv_schedule_update_message_type_validation_on_parsing_parametrizer
)


def test_create_from_pv_schedule_update_signed_change_request_message(
    pv_schedule_update_signed_change_request_message, regular_node_key_pair
):
    signed_change_request = SignedChangeRequest.create_from_signed_change_request_message(
        message=pv_schedule_update_signed_change_request_message,
        signing_key=regular_node_key_pair.private,
    )
    assert isinstance(signed_change_request, PVScheduleUpdateSignedChangeRequest)
    assert signed_change_request.message == pv_schedule_update_signed_change_request_message
    assert signed_change_request.signer == regular_node_key_pair.public
    assert signed_change_request.signature == (
        '2e2ee47f64f59faab40e7166bd34508e3a8d942d13efa39ffdaaf012d0f9f462'
        'f34449bed87e3bc909164c03173483ea33c641ade39d95ed9f0c977f78c2760c'
    )


def test_serialize_and_deserialize_pv_schedule_update(pv_schedule_update_signed_change_request):
    assert isinstance(pv_schedule_update_signed_change_request, PVScheduleUpdateSignedChangeRequest)
    serialized = pv_schedule_update_signed_change_request.json()
    deserialized = SignedChangeRequest.parse_raw(serialized)
    assert isinstance(deserialized, PVScheduleUpdateSignedChangeRequest)
    assert deserialized.signer == pv_schedule_update_signed_change_request.signer
    assert deserialized.signature == pv_schedule_update_signed_change_request.signature
    assert deserialized.message == pv_schedule_update_signed_change_request.message
    assert deserialized == pv_schedule_update_signed_change_request

    serialized2 = deserialized.json()
    assert serialized == serialized2


@pv_schedule_update_message_type_validation_on_parsing_parametrizer
def test_type_validation_for_pv_schedule_update_message_on_parsing(
    id_, account_lock, schedule_block_number, node_identifier, search_re, regular_node_key_pair
):
    if node_identifier is VALID:
        node_identifier = regular_node_key_pair.public
    serialized = {
        'signer': '0' * 64,
        'signature': '0' * 128,
        'message': {
            'type': 3,
            'account_lock': '0' * 64 if account_lock is VALID else account_lock,
            'schedule': {
                '1' if schedule_block_number is VALID else schedule_block_number: node_identifier
            }
        }
    }
    serialized_json = json.dumps(serialized)
    with pytest.raises(PydanticValidationError) as exc_info:
        SignedChangeRequest.parse_raw(serialized_json)

    assert re.search(search_re, str(exc_info.value), flags=re.DOTALL)

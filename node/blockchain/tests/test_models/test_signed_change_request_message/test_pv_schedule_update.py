import json
import re

import pytest
from django.conf import settings
from pydantic import ValidationError as PydanticValicationError

from node.blockchain.inner_models.signed_change_request_message import PVScheduleUpdateSignedChangeRequestMessage
from node.blockchain.tests.test_models.base import (
    VALID, pv_schedule_update_message_type_validation_on_instantiation_parametrizer,
    pv_schedule_update_message_type_validation_on_parsing_parametrizer
)
from node.blockchain.types import Type
from node.core.exceptions import ValidationError


def test_create_pv_schedule_update_signed_change_request_message(pv_schedule_update_signed_change_request_message):
    assert pv_schedule_update_signed_change_request_message.type == Type.PV_SCHEDULE_UPDATE


def test_schedule_keys_as_numbers_should_rais_error():
    with pytest.raises(PydanticValicationError, match='str type expected'):
        PVScheduleUpdateSignedChangeRequestMessage(
            schedule={
                0: '0' * 64,
            },
            account_lock='0' * 64,
        )


def test_schedule_contain_at_least_one_element():
    with pytest.raises(ValidationError, match='Schedule should contain at least one element'):
        PVScheduleUpdateSignedChangeRequestMessage(
            schedule={},
            account_lock='0' * 64,
        )


def test_schedule_capacity():
    with pytest.raises(
        ValidationError, match=f'Schedule should contain not more than {settings.NODE_SCHEDULE_CAPACITY} elements'
    ):
        PVScheduleUpdateSignedChangeRequestMessage(
            schedule={str(n): (str(n) * 64)[:64] for n in range(settings.NODE_SCHEDULE_CAPACITY + 1)},
            account_lock='0' * 64,
        )


@pv_schedule_update_message_type_validation_on_instantiation_parametrizer
def test_type_validation_on_instantiation(
    id_, account_lock, schedule_block_number, node_identifier, search_re, regular_node_key_pair
):
    with pytest.raises(PydanticValicationError) as exc_info:
        if node_identifier is VALID:
            node_identifier = regular_node_key_pair.public

        PVScheduleUpdateSignedChangeRequestMessage(
            account_lock='0' * 64 if account_lock is VALID else account_lock,
            schedule={'1' if schedule_block_number is VALID else schedule_block_number: node_identifier}
        )
    assert re.search(search_re, str(exc_info.value), flags=re.DOTALL)


@pv_schedule_update_message_type_validation_on_parsing_parametrizer
def test_type_validation_on_parsing(
    id_, account_lock, schedule_block_number, node_identifier, search_re, regular_node_key_pair
):
    if node_identifier is VALID:
        node_identifier = regular_node_key_pair.public
    serialized = {
        'account_lock': '0' * 64 if account_lock is VALID else account_lock,
        'schedule': {
            '1' if schedule_block_number is VALID else schedule_block_number: node_identifier
        }
    }
    serialized_json = json.dumps(serialized)
    with pytest.raises(PydanticValicationError) as exc_info:
        PVScheduleUpdateSignedChangeRequestMessage.parse_raw(serialized_json)

    assert re.search(search_re, str(exc_info.value), flags=re.DOTALL)

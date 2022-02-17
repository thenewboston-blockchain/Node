import pytest
from django.conf import settings
from pydantic import ValidationError as PydanticValicationError

from node.blockchain.inner_models.signed_change_request_message import PVScheduleUpdateSignedChangeRequestMessage
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
        ValidationError, match=f'Schedule should contain not more than {settings.SCHEDULE_CAPACITY} elements'
    ):
        PVScheduleUpdateSignedChangeRequestMessage(
            schedule={str(n): (str(n) * 64)[:64] for n in range(settings.SCHEDULE_CAPACITY + 1)},
            account_lock='0' * 64,
        )

from django.conf import settings
from pydantic import Field, validator

from node.core.exceptions import ValidationError
from node.core.utils.types import intstr

from ...types import AccountNumber, Type
from .base import SignedChangeRequestMessage


class PVScheduleUpdateSignedChangeRequestMessage(SignedChangeRequestMessage):
    schedule: dict[intstr, AccountNumber]
    type: Type = Field(default=Type.PV_SCHEDULE_UPDATE, const=True)  # noqa: A003

    @validator('schedule')
    def should_not_be_empty(cls, schedule):
        if not schedule:
            raise ValidationError('Schedule should contain at least one element')
        return schedule

    @validator('schedule')
    def should_contain_not_more_elements(cls, schedule):
        if len(schedule) > (schedule_capacity := settings.SCHEDULE_CAPACITY):
            raise ValidationError(f'Schedule should contain not more than {schedule_capacity} elements')
        return schedule

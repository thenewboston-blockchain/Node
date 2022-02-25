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

    def validate_nodes_are_declared(self, blockchain_facade):
        for node_identifier in self.schedule.values():
            if not blockchain_facade.get_node_by_identifier(node_identifier):
                raise ValidationError('All nodes in the schedule must be declared')

    def validate_block_numbers(self, blockchain_facade):
        if min(int(key) for key in self.schedule.keys()) < blockchain_facade.get_next_block_number():
            raise ValidationError('Schedule keys must be equal or more than next block number')

    def validate_blockchain_state_dependent(self, blockchain_facade):
        super().validate_blockchain_state_dependent(blockchain_facade)
        self.validate_nodes_are_declared(blockchain_facade)
        self.validate_block_numbers(blockchain_facade)

from django.conf import settings
from pydantic import Field, validator

from node.core.exceptions import ValidationError
from node.core.utils.types import non_negative_intstr

from ...types import AccountNumber, Type
from .base import SignedChangeRequestMessage


class PVScheduleUpdateSignedChangeRequestMessage(SignedChangeRequestMessage):
    schedule: dict[non_negative_intstr, AccountNumber]
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
        insertion_point = blockchain_facade.get_insertion_point(
            self.schedule, blockchain_facade.get_next_block_number()
        )
        if insertion_point < 1:
            raise ValidationError('Schedule with lowest key must cover next block number')

        if insertion_point > 1:
            raise ValidationError('Outdated block numbers detected in schedule')

    def validate_blockchain_state_dependent(self, blockchain_facade):
        super().validate_blockchain_state_dependent(blockchain_facade)
        self.validate_nodes_are_declared(blockchain_facade)
        self.validate_block_numbers(blockchain_facade)

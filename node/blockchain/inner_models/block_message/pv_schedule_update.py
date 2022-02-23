from pydantic import Field

from node.blockchain.inner_models.signed_change_request import PVScheduleUpdateSignedChangeRequest

from ...types import Type
from .base import BlockMessage, BlockMessageUpdate


class PVScheduleUpdateBlockMessage(BlockMessage):
    type: Type = Field(default=Type.PV_SCHEDULE_UPDATE, const=True)  # noqa: A003
    request: PVScheduleUpdateSignedChangeRequest

    @classmethod
    def make_block_message_update(
        cls, request: PVScheduleUpdateSignedChangeRequest, blockchain_facade
    ) -> BlockMessageUpdate:
        return BlockMessageUpdate(schedule=request.message.schedule)

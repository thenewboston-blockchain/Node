from typing import Optional

from pydantic import Field, StrictBool, StrictStr

from node.blockchain.mixins.validatable import ValidatableMixin
from node.core.utils.types import positive_int

from ...types import AccountNumber, Type
from ..base import BaseModel
from .base import SignedChangeRequestMessage


class CoinTransferTransaction(ValidatableMixin, BaseModel):
    recipient: AccountNumber
    is_fee: Optional[StrictBool] = Field(default=False)
    amount: positive_int
    memo: Optional[StrictStr] = Field(default=None)


class CoinTransferSignedChangeRequestMessage(SignedChangeRequestMessage):
    txs: list[CoinTransferTransaction]
    type: Type = Field(default=Type.COIN_TRANSFER, const=True)  # noqa: A003

    def validate_business_logic(self):
        super().validate_business_logic()
        # TODO(dmu) CRITICAL: Implement in https://thenewboston.atlassian.net/browse/BC-217

    def validate_blockchain_state_dependent(self, blockchain_facade):
        super().validate_blockchain_state_dependent(blockchain_facade)
        # TODO(dmu) CRITICAL: Implement in https://thenewboston.atlassian.net/browse/BC-217

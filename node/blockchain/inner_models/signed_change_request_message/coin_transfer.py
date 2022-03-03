from typing import Optional

from pydantic import Field, StrictBool, StrictStr, validator

from node.blockchain.mixins.validatable import ValidatableMixin
from node.core.exceptions import ValidationError
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

    @validator('txs')
    def has_at_least_one_transaction(cls, txs):
        if not txs:
            raise ValidationError('Request should contain at least one transaction')
        return txs

    def get_total_amount(self):
        return sum(tx.amount for tx in self.txs)

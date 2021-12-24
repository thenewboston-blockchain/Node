from typing import Any
from typing import Type as TypingType
from typing import TypeVar

from pydantic import Field

from node.blockchain.inner_models.base import BaseModel

from ...types import AlphaAccountLock, AlphaAccountNumber, Type
from .base import SignedChangeRequestMessage

T = TypeVar('T', bound='GenesisSignedChangeRequestMessage')


class AlphaAccount(BaseModel):
    balance: int
    balance_lock: AlphaAccountLock


class GenesisSignedChangeRequestMessage(SignedChangeRequestMessage):
    accounts: dict[AlphaAccountNumber, AlphaAccount]
    type: Type = Field(default=Type.GENESIS, const=True)  # noqa: A003

    @classmethod
    def create_from_treasury_account(
        cls: TypingType[T],
        *,
        account_lock: AlphaAccountLock,
        treasury_account_number: AlphaAccountNumber,
        treasury_amount: int = 281474976710656
    ) -> T:
        return cls(
            account_lock=account_lock,
            accounts={
                treasury_account_number: AlphaAccount(balance=treasury_amount, balance_lock=treasury_account_number)
            }
        )

    @classmethod
    def create_from_alpha_account_root_file(
        cls: TypingType[T], *, account_lock: AlphaAccountLock, account_root_file: dict[str, Any]
    ):
        accounts = {}
        for account_number, account_state in account_root_file.items():
            accounts[account_number] = AlphaAccount(
                balance=account_state['balance'], balance_lock=account_state['balance_lock']
            )

        return cls(account_lock=account_lock, accounts=accounts)

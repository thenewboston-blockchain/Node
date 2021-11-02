from dataclasses import dataclass


@dataclass
class AccountState:
    balance: int
    balance_lock: str

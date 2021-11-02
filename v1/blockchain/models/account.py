from dataclasses import dataclass


@dataclass
class Account:
    balance: int
    balance_lock: str

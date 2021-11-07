from dataclasses import dataclass


@dataclass
class Account:
    balance: int
    lock: str

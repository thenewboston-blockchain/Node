from dataclasses import dataclass


@dataclass
class AlphaAccount:
    balance: int
    balance_lock: str

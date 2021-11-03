from dataclasses import dataclass


@dataclass
class BaseBlockMessage:
    block_identifier: str
    block_number: int
    block_type: str
    timestamp: str
    updates: dict

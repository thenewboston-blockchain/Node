from dataclasses import dataclass
from typing import Optional


@dataclass
class BaseBlockMessage:
    block_identifier: Optional[str]
    block_number: int
    block_type: str
    timestamp: str
    updates: dict

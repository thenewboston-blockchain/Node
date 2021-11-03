from dataclasses import dataclass
from datetime import datetime


@dataclass
class BaseBlock:
    block_identifier: str
    block_number: int
    block_type: str
    timestamp: datetime
    updates: dict

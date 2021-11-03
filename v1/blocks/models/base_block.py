from dataclasses import dataclass
from datetime import datetime


@dataclass
class BaseBlock:
    block_identifier: str
    block_number: int
    timestamp: datetime
    updates: dict

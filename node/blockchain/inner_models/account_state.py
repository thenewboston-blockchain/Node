from typing import Optional

from node.core.utils.types import AccountLock

from .base import BaseModel
from .node import Node


class AccountState(BaseModel):
    balance: Optional[int]
    account_lock: Optional[AccountLock]
    node: Optional[Node]

from typing import Optional

from node.core.utils.types import Hash

from .base import BaseModel
from .node import Node


class AccountState(BaseModel):
    balance: Optional[int]
    account_lock: Optional[Hash]
    node: Optional[Node]

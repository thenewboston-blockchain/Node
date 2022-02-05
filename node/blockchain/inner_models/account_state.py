from typing import Optional

from node.core.utils.types import non_negative_int

from ..types import AccountLock
from .base import BaseModel
from .node import Node


class AccountState(BaseModel):
    balance: Optional[non_negative_int]
    # TODO(dmu) MEDIUM: Consider making account_lock mandatory
    account_lock: Optional[AccountLock]
    node: Optional[Node]

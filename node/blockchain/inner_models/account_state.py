from typing import Optional

from pydantic import root_validator

from node.core.exceptions import ValidationError
from node.core.utils.types import non_negative_int

from ..types import AccountLock
from .base import BaseModel
from .node import Node


class AccountState(BaseModel):
    balance: Optional[non_negative_int]
    # TODO(dmu) MEDIUM: Consider making account_lock mandatory
    account_lock: Optional[AccountLock]
    node: Optional[Node]

    @root_validator
    def even_one_is_not_none(cls, values):
        if not values['balance'] and not values['node']:
            raise ValidationError('At least one attribute of AccountState should not be empty')
        return values

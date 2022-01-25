from pydantic import AnyUrl

from node.core.utils.types import non_negative_int

from ..types import AccountNumber
from .base import BaseModel


class Node(BaseModel):
    identifier: AccountNumber
    addresses: list[AnyUrl]
    fee: non_negative_int

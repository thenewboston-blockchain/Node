from pydantic import AnyUrl

from node.core.utils.types import AccountNumber, positive_int

from .base import BaseModel


class Node(BaseModel):
    identifier: AccountNumber
    addresses: list[AnyUrl]
    fee: positive_int

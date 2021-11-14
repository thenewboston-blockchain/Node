from node.core.utils.types import AccountNumber

from .base import BaseModel


class Node(BaseModel):
    identifier: AccountNumber
    addresses: list[str]
    fee: int

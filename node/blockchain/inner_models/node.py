from pydantic import AnyUrl

from node.core.utils.types import positive_int

from ..types import AccountNumber
from .base import BaseModel


class Node(BaseModel):
    identifier: AccountNumber
    addresses: list[AnyUrl]
    fee: positive_int

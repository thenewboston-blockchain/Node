from dataclasses import dataclass

from v1.accounts.models.account import Account
from .node import Node


@dataclass
class Snapshot:
    accounts: dict[str, Account]
    nodes: dict[str, Node]
    last_block_number: int

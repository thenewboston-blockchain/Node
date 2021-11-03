from dataclasses import dataclass

from .node import Node


@dataclass
class Snapshot:
    accounts: dict[str, dict]
    nodes: dict[str, Node]

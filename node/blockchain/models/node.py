from djongo import models

from node.blockchain.inner_models import Node as PydanticNode
from node.core.fields import NullableJSONField

from ..types import NodeRole
from .account_state import AccountState


class Node(AccountState):
    NODE_ROLE = [(r.value, r.name) for r in NodeRole]

    addresses = NullableJSONField(blank=True, null=True)
    fee = models.PositiveBigIntegerField(default=0)
    block_number = models.PositiveBigIntegerField('Block number', blank=True, null=True)
    role = models.PositiveSmallIntegerField(choices=NODE_ROLE, default=NodeRole.REGULAR_NODE.value)

    def get_node(self) -> PydanticNode:
        return PydanticNode(
            identifier=self.identifier,
            addresses=self.addresses,
            fee=self.fee,
        )

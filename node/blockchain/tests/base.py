from contextlib import contextmanager

from node.blockchain.facade import BlockchainFacade
from node.blockchain.models import Node
from node.blockchain.types import NodeRole
from node.core.utils.cryptography import get_node_identifier


@contextmanager
def as_role(node_role: NodeRole):
    next_block_number = BlockchainFacade.get_instance().get_next_block_number()
    node_identifier = get_node_identifier()
    if node_role == NodeRole.PRIMARY_VALIDATOR:
        Node.objects.filter(role=NodeRole.PRIMARY_VALIDATOR.value
                            ).update(role=NodeRole.REGULAR_NODE.value, block_number=None)
        Node.objects.update_or_create(
            identifier=node_identifier,
            defaults={
                'block_number': next_block_number,
                'role': NodeRole.PRIMARY_VALIDATOR.value
            }
        )
    elif node_role == NodeRole.CONFIRMATION_VALIDATOR:
        pv = Node.objects.filter(block_number__lte=next_block_number).order_by('-block_number').first()
        assert pv is None or pv.identifier != node_identifier
        Node.objects.update_or_create(
            identifier=node_identifier,
            defaults={
                'block_number': next_block_number + 10,
                'role': NodeRole.CONFIRMATION_VALIDATOR.value
            }
        )
    else:
        assert node_role == NodeRole.REGULAR_NODE
        Node.objects.filter(identifier=node_identifier).update(role=NodeRole.REGULAR_NODE.value, block_number=None)
    yield

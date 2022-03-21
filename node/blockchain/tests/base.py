from contextlib import contextmanager

from node.blockchain.facade import BlockchainFacade
from node.blockchain.models import Schedule
from node.blockchain.types import NodeRole
from node.core.utils.cryptography import get_node_identifier


def make_node_as_role(node_identifier, node_role):
    next_block_number = BlockchainFacade.get_instance().get_next_block_number()
    if node_role == NodeRole.PRIMARY_VALIDATOR:
        Schedule.objects.update_or_create(_id=next_block_number, defaults={'node_identifier': node_identifier})
    elif node_role == NodeRole.CONFIRMATION_VALIDATOR:
        pv = Schedule.objects.filter(_id__lte=next_block_number).order_by('-_id').first()
        assert pv is None or pv.node_identifier != node_identifier
        Schedule.objects.update_or_create(_id=next_block_number + 10, defaults={'node_identifier': node_identifier})
    else:
        assert node_role == NodeRole.REGULAR_NODE
        Schedule.objects.filter(node_identifier=node_identifier).delete()


@contextmanager
def as_role(node_role: NodeRole):
    make_node_as_role(get_node_identifier(), node_role)
    yield

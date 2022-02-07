from contextlib import contextmanager

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import Node, NodeDeclarationSignedChangeRequestMessage, SignedChangeRequest
from node.blockchain.models import Schedule
from node.blockchain.types import KeyPair, NodeRole
from node.core.utils.cryptography import get_node_identifier


@contextmanager
def as_role(node_role: NodeRole):
    next_block_number = BlockchainFacade.get_instance().get_next_block_number()
    node_identifier = get_node_identifier()
    if node_role == NodeRole.PRIMARY_VALIDATOR:
        Schedule.objects.update_or_create(_id=next_block_number, defaults={'node_identifier': node_identifier})
    elif node_role == NodeRole.CONFIRMATION_VALIDATOR:
        pv = Schedule.objects.filter(_id__lte=next_block_number).order_by('-_id').first()
        assert pv is None or pv.node_identifier != node_identifier
        Schedule.objects.update_or_create(_id=next_block_number + 10, defaults={'node_identifier': node_identifier})
    else:
        assert node_role == NodeRole.REGULAR_NODE
        Schedule.objects.filter(node_identifier=node_identifier).delete()

    yield


def get_node_declaration_signed_change_request(node: Node, node_key_pair: KeyPair) -> SignedChangeRequest:
    message = NodeDeclarationSignedChangeRequestMessage(
        node=node,
        account_lock=node.identifier,
    )

    signed_change_request = SignedChangeRequest.create_from_signed_change_request_message(
        message=message,
        signing_key=node_key_pair.private,
    )
    assert signed_change_request.message
    assert signed_change_request.signer
    assert signed_change_request.signature

    return signed_change_request

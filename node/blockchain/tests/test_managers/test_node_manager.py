import pytest

from node.blockchain.models import Node
from node.blockchain.types import NodeRole


@pytest.mark.parametrize(
    'roles, node_args', (
        (None, ()),
        ((), ()),
        ((NodeRole.REGULAR_NODE, NodeRole.PRIMARY_VALIDATOR, NodeRole.CONFIRMATION_VALIDATOR), (
            'primary_validator_node', 'regular_node', 'self_node', 'confirmation_validator_node',
            'confirmation_validator_node_2'
        )),
        ((NodeRole.REGULAR_NODE,), ('regular_node', 'self_node')),
        ((NodeRole.PRIMARY_VALIDATOR,), ('primary_validator_node',)),
        ((NodeRole.CONFIRMATION_VALIDATOR,), ('confirmation_validator_node', 'confirmation_validator_node_2')),
        ((NodeRole.PRIMARY_VALIDATOR, NodeRole.CONFIRMATION_VALIDATOR),
         ('primary_validator_node', 'confirmation_validator_node', 'confirmation_validator_node_2')),
        ((
            NodeRole.REGULAR_NODE,
            NodeRole.PRIMARY_VALIDATOR,
        ), (
            'regular_node',
            'self_node',
            'primary_validator_node',
        )),
        ((
            NodeRole.REGULAR_NODE,
            NodeRole.CONFIRMATION_VALIDATOR,
        ), (
            'regular_node',
            'self_node',
            'confirmation_validator_node',
            'confirmation_validator_node_2',
        )),
    )
)
@pytest.mark.usefixtures('rich_blockchain')
def test_filter_by_roles(
    roles, node_args, primary_validator_node, regular_node, self_node, confirmation_validator_node,
    confirmation_validator_node_2
):
    nodes = set()
    for name in node_args:
        nodes.add(locals()[name].identifier)

    assert set(item._id for item in Node.objects.all().filter_by_roles(roles)) == nodes

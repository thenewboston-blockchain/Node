from contextlib import contextmanager
from unittest.mock import patch

from node.blockchain.types import NodeRole


@contextmanager
def as_role(node_role: NodeRole):
    with patch('node.blockchain.facade.BlockchainFacade.get_node_role', return_value=node_role):
        yield

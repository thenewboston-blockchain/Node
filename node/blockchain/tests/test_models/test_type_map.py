from node.blockchain.inner_models import (
    GenesisBlockMessage, GenesisSignedChangeRequest, NodeDeclarationBlockMessage, NodeDeclarationSignedChangeRequest
)
from node.blockchain.inner_models.type_map import get_block_message_subclass, get_signed_change_request_subclass
from node.blockchain.types import Type


def test_get_block_message_subclass():
    assert get_block_message_subclass(Type.GENESIS) == GenesisBlockMessage
    assert get_block_message_subclass(Type.NODE_DECLARATION) == NodeDeclarationBlockMessage


def test_get_signed_change_request_subclass():
    assert get_signed_change_request_subclass(Type.GENESIS) == GenesisSignedChangeRequest
    assert get_signed_change_request_subclass(Type.NODE_DECLARATION) == NodeDeclarationSignedChangeRequest

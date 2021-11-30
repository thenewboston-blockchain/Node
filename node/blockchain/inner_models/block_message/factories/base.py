from datetime import datetime
from node.blockchain.inner_models.signed_change_request import (
    GenesisSignedChangeRequest, NodeDeclarationSignedChangeRequest, SignedChangeRequest
)
from node.blockchain.inner_models.block_message.base import BlockMessage, BlockMessageUpdate
from . import genesis, node_declaration
from node.core.utils.types import Type


TYPE_MAP = {
    Type.GENESIS: genesis.make_block_message_update_from_signed_change_request,
    Type.NODE_DECLARATION: node_declaration.make_block_message_update_from_signed_change_request,
}


def make_block_message_update_from_signed_change_request(request: SignedChangeRequest, **kwargs) -> BlockMessageUpdate:
    func = TYPE_MAP.get(request.message.type)
    return func(request, **kwargs)


def make_block_message_from_signed_change_request(request: SignedChangeRequest, **kwargs) -> BlockMessage:
    now = datetime.utcnow()
    update = make_block_message_update_from_signed_change_request(request, **kwargs)
    return cls(
        timestamp=now,
        request=request,
        update=update,
    )

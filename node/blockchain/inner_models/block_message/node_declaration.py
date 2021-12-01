from pydantic import Field

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models.signed_change_request import NodeDeclarationSignedChangeRequest
from node.core.utils.types import Type

from .base import BlockMessage, BlockMessageUpdate


class NodeDeclarationBlockMessage(BlockMessage):
    type: Type = Field(default=Type.NODE_DECLARATION, const=True)  # noqa: A003
    request: NodeDeclarationSignedChangeRequest

    @classmethod
    def make_block_message_update(
        cls, request: NodeDeclarationSignedChangeRequest, blockchain_facade: BlockchainFacade
    ) -> BlockMessageUpdate:
        # TODO(dmu) CRITICAL: Implement this method
        #                     https://thenewboston.atlassian.net/browse/BC-77
        raise NotImplementedError()

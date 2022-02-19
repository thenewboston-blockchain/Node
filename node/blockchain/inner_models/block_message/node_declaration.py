from pydantic import Field

from node.blockchain.inner_models import AccountState
from node.blockchain.inner_models.signed_change_request import NodeDeclarationSignedChangeRequest

from ...types import Type
from .base import BlockMessage, BlockMessageUpdate


class NodeDeclarationBlockMessage(BlockMessage):
    type: Type = Field(default=Type.NODE_DECLARATION, const=True)  # noqa: A003
    request: NodeDeclarationSignedChangeRequest

    @classmethod
    def make_block_message_update(
        cls, request: NodeDeclarationSignedChangeRequest, blockchain_facade
    ) -> BlockMessageUpdate:
        account_state = AccountState(
            account_lock=request.make_hash(),
            node=request.message.node,
        )
        accounts = {request.signer: account_state}
        return BlockMessageUpdate(accounts=accounts)

    class Config(BlockMessage.Config):
        exclude = {'request': {'message': {'node': {'identifier': ...}}}}
        enrich = {'request.message.node.identifier': 'request.signer'}

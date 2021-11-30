from typing import Type as TypingType
from typing import TypeVar

from pydantic import Field

from node.blockchain.inner_models.signed_change_request import NodeDeclarationSignedChangeRequest
from node.core.utils.types import Type

from .base import BlockMessage

NodeDeclarationBlockMessageT = TypeVar('NodeDeclarationBlockMessageT', bound='NodeDeclarationBlockMessage')


class NodeDeclarationBlockMessage(BlockMessage):
    type: Type = Field(default=Type.NODE_DECLARATION, const=True)  # noqa: A003
    request: NodeDeclarationSignedChangeRequest

    @classmethod
    def create_from_signed_change_request(
        cls: TypingType[NodeDeclarationBlockMessageT], request: NodeDeclarationSignedChangeRequest
    ) -> NodeDeclarationBlockMessageT:
        raise NotImplementedError

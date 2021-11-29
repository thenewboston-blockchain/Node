from typing import Type as TypingType
from typing import TypeVar

from node.blockchain.inner_models.signed_change_request import NodeDeclarationSignedChangeRequest

from .base import BlockMessage

T = TypeVar('T', bound='NodeDeclarationBlockMessage')


class NodeDeclarationBlockMessage(BlockMessage):
    request: NodeDeclarationSignedChangeRequest

    @classmethod
    def create_from_signed_change_request(cls: TypingType[T], request: NodeDeclarationSignedChangeRequest) -> T:
        raise NotImplementedError

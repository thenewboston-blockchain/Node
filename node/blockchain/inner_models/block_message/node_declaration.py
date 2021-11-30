from typing import Type as TypingType
from typing import TypeVar

from node.blockchain.inner_models.signed_change_request import NodeDeclarationSignedChangeRequest

from .base import BlockMessage, BlockMessageUpdate

T = TypeVar('T', bound='NodeDeclarationBlockMessage')
U = TypeVar('U', bound='NodeDeclarationBlockMessageUpdate')


class NodeDeclarationBlockMessageUpdate(BlockMessageUpdate):
    @classmethod
    def create_from_signed_change_request(cls: TypingType[U], request: NodeDeclarationSignedChangeRequest) -> U:
        raise NotImplementedError


class NodeDeclarationBlockMessage(BlockMessage):
    request: NodeDeclarationSignedChangeRequest

    @classmethod
    def create_from_signed_change_request(cls: TypingType[T], request: NodeDeclarationSignedChangeRequest) -> T:
        raise NotImplementedError

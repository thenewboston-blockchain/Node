from pydantic import Field

from node.core.utils.types import Type

from ..node import Node
from .base import SignedChangeRequestMessage


class NodeDeclarationSignedChangeRequestMessage(SignedChangeRequestMessage):
    node: Node
    type: Type = Field(default=Type.NODE_DECLARATION, const=True)  # noqa: A003

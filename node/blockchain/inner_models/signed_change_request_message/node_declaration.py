from pydantic import Field

from ...types import Type
from ..node import Node
from .base import SignedChangeRequestMessage


class NodeDeclarationSignedChangeRequestMessage(SignedChangeRequestMessage):
    node: Node
    type: Type = Field(default=Type.NODE_DECLARATION, const=True)  # noqa: A003

    class Config(SignedChangeRequestMessage.Config):
        exclude_crypto = {'node': {'identifier': ...}}

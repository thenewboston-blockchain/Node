from pydantic import Field

from ...types import Type
from ..node import Node
from .base import SignedChangeRequestMessage


class NodeDeclarationSignedChangeRequestMessage(SignedChangeRequestMessage):
    node: Node
    type: Type = Field(default=Type.NODE_DECLARATION, const=True)  # noqa: A003

    def validate_business_logic(self):
        super().validate_business_logic()
        # TODO(dmu) MEDIUM: Do we need to add anything here?

    def validate_blockchain_state_dependent(self, blockchain_facade):
        super().validate_blockchain_state_dependent(blockchain_facade)
        # TODO(dmu) MEDIUM: Do we need to add anything here?

    class Config(SignedChangeRequestMessage.Config):
        exclude_crypto = {'node': {'identifier': ...}}

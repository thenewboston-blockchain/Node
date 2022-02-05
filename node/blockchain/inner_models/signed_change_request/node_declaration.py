from typing import TypeVar

from node.core.exceptions import ValidationError

from ..signed_change_request_message import NodeDeclarationSignedChangeRequestMessage
from .base import SignedChangeRequest

T = TypeVar('T', bound='SignedChangeRequest')


class NodeDeclarationSignedChangeRequest(SignedChangeRequest):
    message: NodeDeclarationSignedChangeRequestMessage

    def validate_business_logic(self):
        # TODO(dmu) MEDIUM: Should we use Pydantic native validation here instead?
        if self.signer != self.message.node.identifier:
            raise ValidationError('Signer does not match with node identifier')

    class Config(SignedChangeRequest.Config):
        exclude = {'message': {'node': {'identifier': ...}}}
        enrich = {'message.node.identifier': 'signer'}

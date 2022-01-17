from typing import TYPE_CHECKING, TypeVar

from node.core.exceptions import ValidationError

from ..signed_change_request_message import NodeDeclarationSignedChangeRequestMessage
from .base import SignedChangeRequest

if TYPE_CHECKING:
    from node.blockchain.facade import BlockchainFacade

T = TypeVar('T', bound='SignedChangeRequest')


class NodeDeclarationSignedChangeRequest(SignedChangeRequest):
    message: NodeDeclarationSignedChangeRequestMessage

    def validate_type_specific_attributes(self, blockchain_facade: 'BlockchainFacade'):
        # TODO(dmu) MEDIUM: Should we use Pydantic native validation here instead?
        if self.signer != self.message.node.identifier:
            raise ValidationError('Signer does not match with node identifier')

    class Config(SignedChangeRequest.Config):
        exclude = {'message': {'node': {'identifier': ...}}}
        enrich = {'message.node.identifier': 'signer'}

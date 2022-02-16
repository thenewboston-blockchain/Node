import logging
import sys

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import NodeDeclarationSignedChangeRequest, NodeDeclarationSignedChangeRequestMessage
from node.core.clients.node import NodeClient
from node.core.commands import CustomCommand
from node.core.utils.cryptography import get_node_identifier, get_signing_key
from node.core.utils.network import make_own_node

logger = logging.getLogger(__name__)


class Command(CustomCommand):
    help = 'Ensure node is declared'  # noqa: A003

    def handle(self, *args, **options):
        facade = BlockchainFacade.get_instance()

        primary_validator = facade.get_primary_validator()
        if not primary_validator:
            self.write_error('No primary validator blockchain detected')
            sys.exit(1)

        node_identifier = get_node_identifier()
        self.write(f'This node identifier: {node_identifier}')

        node = make_own_node()
        if declared_node := facade.get_node_by_identifier(node_identifier):
            if declared_node == node:
                self.write_success('Node is already declared')
                return

            self.write(f'Node is declared as {declared_node}, but needs to be declared as {node}')
        else:
            self.write('Node is not declared yet')

        message = NodeDeclarationSignedChangeRequestMessage(
            node=node,
            account_lock=facade.get_account_lock(node_identifier),
        )
        request = NodeDeclarationSignedChangeRequest.create_from_signed_change_request_message(
            message, get_signing_key()
        )

        self.write(f'Sending node declaration request: {request}')
        NodeClient.get_instance().send_signed_change_request(primary_validator, request)
        self.write_success('Node declaration request has been sent')

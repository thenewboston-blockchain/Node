import json
import sys

from node.blockchain.inner_models import (
    CoinTransferSignedChangeRequestMessage, Node, NodeDeclarationSignedChangeRequestMessage, SignedChangeRequest
)
from node.blockchain.inner_models.signed_change_request_message import CoinTransferTransaction
from node.blockchain.types import AccountNumber, SigningKey, Type
from node.core.clients.node import NodeClient
from node.core.management import CustomCommand
from node.core.utils.cryptography import derive_public_key


class Command(CustomCommand):
    help = 'Submit signed change requests of different types'  # noqa: A003

    def add_arguments(self, parser):
        parser.add_argument('--node-address', type=str, help='Network address of Node')
        parser.add_argument('--signing-key', type=SigningKey, help='Signing (private) key')

        subparsers = parser.add_subparsers(dest='scr_type_name', required=True)

        # Node Declaration
        node_declaration_parser = subparsers.add_parser(
            Type.NODE_DECLARATION.name, help='Node declaration signed change request'
        )
        node_declaration_parser.add_argument('--identifier', type=AccountNumber, required=True, help='Node identifier')
        node_declaration_parser.add_argument(
            '--address', type=str, action='append', required=True, dest='addresses', help='Node network address'
        )
        node_declaration_parser.add_argument('--fee', type=int, required=True, help='Node fee amount')

        # Coin Transfer
        coin_transfer_parser = subparsers.add_parser(
            Type.COIN_TRANSFER.name, help='Coin transfer signed change request'
        )
        coin_transfer_parser.add_argument(
            '--tx', type=self.loads_transaction, dest='txs', action='append', required=True, help='Transaction JSON'
        )

    def loads_transaction(self, transaction):
        return json.loads(transaction)

    def handle(self, node_address: str, signing_key: SigningKey, scr_type_name: str, *args, **options):
        node = Node(identifier='0' * 64, addresses=[node_address], fee=0)
        node_client = NodeClient.get_instance()

        account_state = node_client.get_account_state(node, derive_public_key(signing_key))
        if account_state is None:
            self.write_error('Node address or signing key are wrong.')
            sys.exit(1)

        scr_arguments = {
            'account_lock': account_state.account_lock,
        }

        if scr_type_name == Type.NODE_DECLARATION.name:
            scr_arguments['node'] = Node(**options)
            scr_message = NodeDeclarationSignedChangeRequestMessage(**scr_arguments)
        elif scr_type_name == Type.COIN_TRANSFER.name:
            scr_arguments['txs'] = [CoinTransferTransaction(**tx) for tx in options['txs']]
            scr_message = CoinTransferSignedChangeRequestMessage(**scr_arguments)

        signed_change_request = SignedChangeRequest.create_from_signed_change_request_message(scr_message, signing_key)

        try:
            response = node_client.send_scr_to_node(node, signed_change_request)
        except ConnectionError as ex:
            self.write_error(str(ex))
            sys.exit(1)

        self.write(json.dumps(response.json()))

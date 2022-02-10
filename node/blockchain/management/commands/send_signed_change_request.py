import json
import logging

from node.blockchain.inner_models import (
    CoinTransferSignedChangeRequestMessage, Node, NodeDeclarationSignedChangeRequestMessage, SignedChangeRequest
)
from node.blockchain.inner_models.signed_change_request_message import CoinTransferTransaction
from node.blockchain.types import AccountNumber, SigningKey, Type
from node.core.clients.node import NodeClient
from node.core.management import CustomCommand
from node.core.utils.cryptography import derive_public_key

logger = logging.getLogger(__name__)


def add_common_args(parser):
    parser.add_argument('node-address', type=str)
    parser.add_argument('signing-key', type=SigningKey)
    parser.add_argument('-d', '--dry-run', action='store_true')


def make_message(type_, account_lock, options):
    kwargs = {'account_lock': account_lock}
    if type_ == Type.NODE_DECLARATION:
        kwargs['node'] = Node(
            identifier=derive_public_key(options['signing-key']),
            fee=options['fee'],
            addresses=options['address'],
        )
        return NodeDeclarationSignedChangeRequestMessage(**kwargs)

    if type_ == Type.COIN_TRANSFER:
        kwargs['txs'] = [CoinTransferTransaction.parse_raw(tx) for tx in options['transaction']]
        return CoinTransferSignedChangeRequestMessage(**kwargs)

    raise NotImplementedError(f'Support for signed change request type {type_} is not implemented')


class Command(CustomCommand):
    help = 'Submit signed change requests of different types'  # noqa: A003

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='type', help='Signed Change Request type')

        # Node Declaration
        node_declaration_parser = subparsers.add_parser(
            str(Type.NODE_DECLARATION.value), help=Type.NODE_DECLARATION.name
        )
        add_common_args(node_declaration_parser)
        node_declaration_parser.add_argument('fee', type=int)
        node_declaration_parser.add_argument('address', nargs='+')

        # Coin Transfer
        coin_transfer_parser = subparsers.add_parser(str(Type.COIN_TRANSFER.value), help=Type.COIN_TRANSFER.name)
        add_common_args(coin_transfer_parser)
        transaction_example = CoinTransferTransaction(recipient=AccountNumber('0' * 64), amount=10,
                                                      memo='For Sam').json()
        coin_transfer_parser.add_argument(
            'transaction', nargs='+', help=f'Transaction JSON (example: {transaction_example})'
        )

    def handle(self, *args, **options):
        node_client = NodeClient.get_instance()

        node_address = options.pop('node-address')
        signing_key = SigningKey(options['signing-key'])
        account_state = node_client.get_account_state(node_address, derive_public_key(signing_key))
        logger.debug('Got %r', account_state)
        assert account_state

        dry_run = options.pop('dry_run')
        type_ = Type(int(options.pop('type')))
        message = make_message(type_, account_state.account_lock, options)

        signed_change_request = SignedChangeRequest.create_from_signed_change_request_message(message, signing_key)

        self.write('Generated signer change request:')
        self.write(json.dumps(signed_change_request.dict(), indent=4))
        if dry_run:
            return

        response = node_client.send_signed_change_request(node_address, signed_change_request)
        self.write('Response (raw):')
        self.write(response.text)

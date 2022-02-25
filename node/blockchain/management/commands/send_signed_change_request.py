import json
import logging

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import (
    CoinTransferSignedChangeRequestMessage, Node, NodeDeclarationSignedChangeRequestMessage,
    PVScheduleUpdateSignedChangeRequestMessage, SignedChangeRequest
)
from node.blockchain.inner_models.signed_change_request_message import CoinTransferTransaction
from node.blockchain.types import AccountNumber, SigningKey, Type
from node.core.clients.node import NodeClient
from node.core.commands import CustomCommand
from node.core.utils.cryptography import derive_public_key, get_node_identifier

logger = logging.getLogger(__name__)

LOCAL_BLOCKCHAIN = 'local'


def add_common_args(parser):
    parser.add_argument('node-address', type=str, help='node address or "local" to denote local blockchain operation')
    parser.add_argument('signing-key', type=SigningKey)
    parser.add_argument('-d', '--dry-run', action='store_true')


def get_account_lock(node_address, type_, signing_key):
    if node_address == LOCAL_BLOCKCHAIN:
        assert type_ == Type.PV_SCHEDULE_UPDATE.value
        return BlockchainFacade.get_instance().get_account_lock(get_node_identifier())

    account_state = NodeClient.get_instance().get_account_state(node_address, derive_public_key(signing_key))
    return account_state.account_lock


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

    if type_ == Type.PV_SCHEDULE_UPDATE:
        kwargs['schedule'] = json.loads(options['schedule'])
        return PVScheduleUpdateSignedChangeRequestMessage(**kwargs)

    raise NotImplementedError(f'Support for signed change request type {type_} is not implemented')


def send_signed_change_request(node_address, signed_change_request, signing_key):
    if node_address == LOCAL_BLOCKCHAIN:
        block = BlockchainFacade.get_instance().add_block_from_signed_change_request(
            signed_change_request=signed_change_request, signing_key=signing_key, validate=True
        )
        return block.message.request.json()

    response = NodeClient.get_instance().send_signed_change_request(node_address, signed_change_request)
    return response.text


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

        # Coin Transfer
        pv_schedule_update_parser = subparsers.add_parser(
            str(Type.PV_SCHEDULE_UPDATE.value), help=Type.PV_SCHEDULE_UPDATE.name
        )
        add_common_args(pv_schedule_update_parser)
        schedule_example = json.dumps({
            '100': AccountNumber('1' * 64),
            '200': AccountNumber('2' * 64),
        })
        pv_schedule_update_parser.add_argument('schedule', help=f'Schedule JSON (example: {schedule_example})')

    def handle(self, *args, **options):
        node_address = options.pop('node-address')
        type_ = Type(int(options.pop('type')))
        signing_key = SigningKey(options['signing-key'])

        account_lock = get_account_lock(node_address, type_, signing_key)
        message = make_message(type_, account_lock, options)
        signed_change_request = SignedChangeRequest.create_from_signed_change_request_message(message, signing_key)

        self.write('Generated signer change request:')
        self.write(json.dumps(signed_change_request.dict(), indent=4))

        if options.pop('dry_run'):
            return

        self.write('Response (raw):')
        self.write(send_signed_change_request(node_address, signed_change_request, signing_key))

import json
import logging

from django.db import transaction

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import (
    CoinTransferSignedChangeRequestMessage, Node, NodeDeclarationSignedChangeRequestMessage,
    PVScheduleUpdateSignedChangeRequestMessage, SignedChangeRequest
)
from node.blockchain.inner_models.signed_change_request_message import CoinTransferTransaction
from node.blockchain.types import AccountNumber, Type
from node.core.clients.node import NodeClient
from node.core.commands import CustomCommand
from node.core.database import is_in_transaction
from node.core.utils.cryptography import derive_public_key, get_signing_key

logger = logging.getLogger(__name__)

LOCAL = 'local'


def add_common_args(parser):
    parser.add_argument('node-address', help='remote node address or "local" to denote local blockchain operation')
    parser.add_argument('signing-key', help='signing key or "local" to denote local node singing key')
    parser.add_argument('-d', '--dry-run', action='store_true')


def get_account_lock_from_local_blockchain(public_key):
    return BlockchainFacade.get_instance().get_account_lock(public_key)


def get_account_lock_from_node(node_address, public_key):
    account_state = NodeClient.get_instance().get_account_state(node_address, public_key)
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


def add_block_from_signed_change_request(signed_change_request):
    return BlockchainFacade.get_instance().add_block_from_signed_change_request(signed_change_request)


def send_signed_change_request(node_address, signed_change_request):
    response = NodeClient.get_instance().send_signed_change_request(node_address, signed_change_request)
    return response.text


class Command(CustomCommand):
    help = 'Submit signed change requests of different types'  # noqa: A003

    @staticmethod
    def add_node_declaration_arguments(subparsers):
        node_declaration_parser = subparsers.add_parser(
            str(Type.NODE_DECLARATION.value), help=Type.NODE_DECLARATION.name
        )
        add_common_args(node_declaration_parser)
        node_declaration_parser.add_argument('fee', type=int)
        node_declaration_parser.add_argument('address', nargs='+')

    @staticmethod
    def add_coin_transfer_arguments(subparsers):
        coin_transfer_parser = subparsers.add_parser(str(Type.COIN_TRANSFER.value), help=Type.COIN_TRANSFER.name)
        add_common_args(coin_transfer_parser)
        transaction_example = CoinTransferTransaction(recipient=AccountNumber('0' * 64), amount=10,
                                                      memo='For Sam').json()
        coin_transfer_parser.add_argument(
            'transaction', nargs='+', help=f'Transaction JSON (example: {transaction_example})'
        )

    @staticmethod
    def add_pv_schedule_arguments(subparsers):
        pv_schedule_update_parser = subparsers.add_parser(
            str(Type.PV_SCHEDULE_UPDATE.value), help=Type.PV_SCHEDULE_UPDATE.name
        )
        add_common_args(pv_schedule_update_parser)
        schedule_example = json.dumps({
            '100': AccountNumber('1' * 64),
            '200': AccountNumber('2' * 64),
        })
        pv_schedule_update_parser.add_argument('schedule', help=f'Schedule JSON (example: {schedule_example})')

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='type', help='Signed Change Request type')
        self.add_node_declaration_arguments(subparsers)
        self.add_coin_transfer_arguments(subparsers)
        self.add_pv_schedule_arguments(subparsers)

    def handle(self, *args, **options):
        node_address = options.pop('node-address')
        type_ = Type(int(options.pop('type')))
        signing_key = options['signing-key']
        if signing_key == LOCAL:
            options['signing-key'] = signing_key = get_signing_key()

        public_key = derive_public_key(signing_key)

        if node_address == LOCAL:
            account_lock = get_account_lock_from_local_blockchain(public_key)
        else:
            account_lock = get_account_lock_from_node(node_address, public_key)

        message = make_message(type_, account_lock, options)
        signed_change_request = SignedChangeRequest.create_from_signed_change_request_message(message, signing_key)

        self.write('Generated signer change request:')
        self.write(json.dumps(signed_change_request.dict(), indent=4))

        if options.pop('dry_run'):
            return

        if node_address == LOCAL:
            if is_in_transaction():
                block = add_block_from_signed_change_request(signed_change_request)
            else:
                with transaction.atomic():
                    block = add_block_from_signed_change_request(signed_change_request)

            self.write(f'Block added to local blockchain: {block}')
        else:
            self.write('Response (raw):')
            self.write(send_signed_change_request(node_address, signed_change_request))

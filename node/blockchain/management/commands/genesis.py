import logging
import sys

from django.db import transaction

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import (
    GenesisBlockMessage, GenesisSignedChangeRequest, GenesisSignedChangeRequestMessage
)
from node.blockchain.models.block import Block
from node.blockchain.types import AccountLock
from node.core.management import CustomCommand
from node.core.utils.cryptography import get_signing_key
from node.core.utils.network import make_own_node, read_source

logger = logging.getLogger(__name__)


class Command(CustomCommand):
    help = 'Create genesis block'  # noqa: A003

    def add_arguments(self, parser):
        # TODO(dmu) MEDIUM: We may need simpler blockchains and with known private key for local testing. Implement
        parser.add_argument('source', help='file path or URL to alpha account root file')
        parser.add_argument('-f', '--force', action='store_true', help='remove existing blockchain if any')

    def handle(self, source, force, **options):
        # TODO(dmu) MEDIUM: Cover this method with unittests
        does_exist = Block.objects.exists()
        if does_exist and not force:
            self.write_error('Blockchain already exists')
            sys.exit(1)

        signing_key = get_signing_key()  # we get signing key here to fail fast in case it is not configured
        self.write_info('Got signing key')

        account_root_file = read_source(source)
        self.write_info('Read source')
        primary_validator_node = make_own_node()
        self.write_info('Made own node')
        request_message = GenesisSignedChangeRequestMessage.create_from_alpha_account_root_file(
            account_lock=AccountLock(primary_validator_node.identifier),
            account_root_file=account_root_file,
        )

        request = GenesisSignedChangeRequest.create_from_signed_change_request_message(request_message, signing_key)
        block_message = GenesisBlockMessage.create_from_signed_change_request(request, primary_validator_node)
        self.write_info('Made genesis block message')

        blockchain_facade = BlockchainFacade.get_instance()

        with transaction.atomic():
            if does_exist:
                Block.objects.all().delete()

            Block.objects.add_block_from_block_message(
                block_message, blockchain_facade, signing_key=signing_key, validate=False
            )

        self.write_success('Blockchain genesis complete')

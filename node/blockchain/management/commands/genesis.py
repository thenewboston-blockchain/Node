import json
import sys
from contextlib import closing
from urllib.parse import urlparse
from urllib.request import urlopen

from django.conf import settings
from django.core.management.base import BaseCommand

from node.blockchain.inner_models import (
    GenesisBlockMessage, GenesisSignedChangeRequestMessage, Node, SignedChangeRequest
)
from node.blockchain.models.block import Block
from node.core.utils.cryptography import derive_public_key
from node.core.utils.types import AccountLock


def is_valid_url(source):
    try:
        parsed = urlparse(source)
        return all((parsed.scheme, parsed.netloc, parsed.path))
    except Exception:
        return False


def read_source(source):
    if is_valid_url(source):
        fo = urlopen(source)
    else:
        fo = open(source)

    with closing(fo) as fo:
        return json.load(fo)


class Command(BaseCommand):
    help = 'Create genesis block'  # noqa: A003

    def add_arguments(self, parser):
        # TODO(dmu) MEDIUM: We may need simpler blockchains and with known private key for local testing. Implement
        parser.add_argument('source', help='file path or URL to alpha account root file')
        parser.add_argument('-f', '--force', action='store_true', help='remove existing blockchain if any')

    def handle(self, source, force, **options):
        does_exist = Block.objects.exists()
        if does_exist and not force:
            self.stdout.write(self.style.ERROR('Blockchain already exists'))
            sys.exit(1)

        account_root_file = read_source(source)
        signing_key = settings.SIGNING_KEY
        account_number = derive_public_key(signing_key)

        request_message = GenesisSignedChangeRequestMessage.create_from_alpha_account_root_file(
            account_lock=AccountLock(account_number),
            account_root_file=account_root_file,
        )

        request = SignedChangeRequest.create_from_signed_change_request_message(
            message=request_message,
            signing_key=signing_key,
        )

        # TODO(dmu) CRITICAL: Autodetect node address
        #                     https://thenewboston.atlassian.net/browse/BC-150
        primary_validator_node = Node(
            identifier=account_number,
            addresses=['http://non-existing-address-4643256.com:8555/'],
            fee=4,
        )

        block_message = GenesisBlockMessage.create_from_signed_change_request(
            request=request,
            primary_validator_node=primary_validator_node,
        )

        # TODO(dmu) MEDIUM: Does happen in transaction?
        if does_exist:
            Block.objects.all().delete()

        Block.objects.create_from_block_message(
            message=block_message,
            signing_key=signing_key,
        )

import json
import logging
import sys
from contextlib import closing
from urllib.parse import urlparse
from urllib.request import urlopen

import stun
from django.conf import settings
from django.core.management.base import BaseCommand

from node.blockchain.inner_models import (
    GenesisBlockMessage, GenesisSignedChangeRequestMessage, Node, SignedChangeRequest
)
from node.blockchain.models.block import Block
from node.core.utils.cryptography import derive_public_key, get_signing_key
from node.core.utils.types import AccountLock

logger = logging.getLogger(__name__)


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


def get_own_network_addresses():
    network_addresses = settings.NODE_NETWORK_ADDRESSES

    if not settings.APPEND_AUTO_DETECTED_NETWORK_ADDRESS:
        return network_addresses

    logger.info('Detecting external IP address')
    try:
        _, external_ip_address, _ = stun.get_ip_info()
    except Exception:
        logger.warning('Unable to detect external IP address')
    else:
        network_address = f'http://{external_ip_address}:{settings.NODE_PORT}/'
        network_addresses = list(network_addresses)
        network_addresses.append(network_address)
    logger.info('External IP address: %s', external_ip_address)
    return network_addresses


def make_own_node():
    return Node(
        identifier=derive_public_key(get_signing_key()), addresses=get_own_network_addresses(), fee=settings.NODE_FEE
    )


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

        signing_key = get_signing_key()

        account_root_file = read_source(source)
        primary_validator_node = make_own_node()
        request_message = GenesisSignedChangeRequestMessage.create_from_alpha_account_root_file(
            account_lock=AccountLock(primary_validator_node.identifier),
            account_root_file=account_root_file,
        )

        request = SignedChangeRequest.create_from_signed_change_request_message(
            message=request_message,
            signing_key=signing_key,
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

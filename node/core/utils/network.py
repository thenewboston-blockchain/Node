import json
import logging
from contextlib import closing
from urllib.parse import urlparse
from urllib.request import urlopen

import stun
from django.conf import settings

from node.blockchain.inner_models import Node
from node.core.utils.cryptography import get_node_identifier

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
        logger.info('External IP address: %s', external_ip_address)
        network_address = f'http://{external_ip_address}:{settings.NODE_PORT}/'
        network_addresses = list(network_addresses)
        network_addresses.append(network_address)

    return network_addresses


def make_own_node():
    return Node(identifier=get_node_identifier(), addresses=get_own_network_addresses(), fee=settings.NODE_FEE)

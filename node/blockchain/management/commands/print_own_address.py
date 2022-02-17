import json
import logging
import sys
from enum import Enum

from node.blockchain.facade import BlockchainFacade
from node.core.commands import CustomCommand
from node.core.utils.cryptography import get_node_identifier
from node.core.utils.network import make_own_node

logger = logging.getLogger(__name__)


class Source(Enum):
    DETECT = 'detect'
    BLOCKCHAIN = 'blockchain'


class Command(CustomCommand):
    help = 'Print own configured address'  # noqa: A003

    def add_arguments(self, parser):
        parser.add_argument('source', choices=[item.value for item in Source])
        parser.add_argument('-i', '--index', type=int)

    def handle(self, *args, source, index=None, **options):
        if source == Source.DETECT.value:
            node = make_own_node()
        else:
            assert source == Source.BLOCKCHAIN.value
            node = BlockchainFacade.get_instance().get_node_by_identifier(get_node_identifier())
            if node is None:
                self.write_error('Node is not declared')
                sys.exit(1)

        if index is None:
            self.write(json.dumps(node.addresses))
        else:
            self.write(node.addresses[index])

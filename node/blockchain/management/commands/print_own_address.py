import json
import logging

from node.core.commands import CustomCommand
from node.core.utils.network import make_own_node

logger = logging.getLogger(__name__)


class Command(CustomCommand):
    help = 'Print own configured address'  # noqa: A003

    def add_arguments(self, parser):
        parser.add_argument('-i', '--index', type=int)

    def handle(self, *args, index=None, **options):
        node = make_own_node()
        if index is None:
            self.write(json.dumps(node.addresses))
        else:
            self.write(node.addresses[index])

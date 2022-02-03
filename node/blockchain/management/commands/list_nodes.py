import json
import logging

from django.core.management.base import BaseCommand

from node.core.clients.node import NodeClient

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Prints list of nodes.'  # noqa: A003

    def add_arguments(self, parser):
        parser.add_argument('node_address')

    def handle(self, node_address: str, *args, **options):
        nodes = [node.dict() for node in NodeClient.get_instance().yield_nodes(node_address)]
        self.stdout.write(json.dumps(nodes, separators=(',', ':')))

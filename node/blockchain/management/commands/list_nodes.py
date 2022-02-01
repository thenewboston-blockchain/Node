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
        node_client = NodeClient.get_instance()
        nodes = []
        for node in node_client.yield_nodes(node_address):
            nodes.append(node.dict())
        self.stdout.write(json.dumps(nodes))

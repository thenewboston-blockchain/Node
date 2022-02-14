import json
import logging

from django.core.management.base import BaseCommand

from node.core.clients.node import NodeClient

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Prints list of nodes'  # noqa: A003

    def add_arguments(self, parser):
        parser.add_argument('node_address')
        parser.add_argument('-f', '--human-friendly', action='store_true')

    def handle(self, node_address: str, *args, **options):
        nodes_generator = NodeClient.get_instance().yield_nodes(node_address)
        if options.get('human_friendly'):
            for node in nodes_generator:
                addresses = ', '.join(node.addresses)
                self.stdout.write(f'- {node.identifier} {addresses} fee={node.fee}')
        else:
            self.stdout.write(json.dumps([node.dict() for node in nodes_generator], separators=(',', ':')))

from django.core.management import BaseCommand

from node.blockchain.utils.network import get_nodes_for_syncing


class Command(BaseCommand):
    help = 'Sync local blockchain with thenewboston blockchain network'  # noqa: A003

    def write_info(self, msg):
        self.stdout.write(msg, self.style.SUCCESS)

    def write_error(self, msg):
        self.stdout.write(msg, self.style.ERROR)

    def get_nodes_for_syncing(self):
        nodes = get_nodes_for_syncing()
        if nodes:
            self.write_info('Got nodes for syncing:')
            for node in nodes:
                addresses = ', '.join(node.addresses)
                self.write_info(f'- {node.identifier}: {addresses}')
        else:
            self.write_error('Nodes for syncing were not found')

        return nodes

    def handle(self, *args, **options):
        nodes = self.get_nodes_for_syncing()
        if not nodes:
            return

        # TODO(dmu) CRITICAL: Implement in https://thenewboston.atlassian.net/browse/BC-164
        raise NotImplementedError

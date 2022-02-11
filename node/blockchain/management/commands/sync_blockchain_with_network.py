import sys

from node.blockchain.facade import BlockchainFacade
from node.blockchain.utils.blockchain_sync import sync_with_node
from node.blockchain.utils.network import get_nodes_for_syncing, get_nodes_majority
from node.core.management import CustomCommand
from node.core.utils.cryptography import get_node_identifier


class Command(CustomCommand):
    help = 'Sync local blockchain with thenewboston blockchain network'  # noqa: A003

    def add_arguments(self, parser):
        # TODO(dmu) MEDIUM: Change formatter class to have defaults printed
        # We need help kwarg to have defaults printed
        parser.add_argument('-g', '--tolerable-gap', type=int, default=10, help='Tolerable gap')
        parser.add_argument('-r', '--max-sync-rounds', type=int, default=10, help='Max sync rounds')

    def get_nodes_for_syncing(self):
        nodes = get_nodes_for_syncing()
        majority = get_nodes_majority(nodes)
        if majority:
            self.write_info(f'Got nodes for syncing (to block number: {majority[0]}):')
            for node in majority[1]:
                addresses = ', '.join(node.addresses)
                self.write_info(f'- {node.identifier}: {addresses}')
        else:
            self.write_error('Nodes for syncing were not found')

        return majority

    def handle(self, tolerable_gap, max_sync_rounds, *args, **options):
        my_identifier = get_node_identifier()
        last_block_number = BlockchainFacade.get_instance().get_next_block_number() - 1
        self.write_info(f'Syncing from block number: {last_block_number + 1}')

        for sync_round in range(max_sync_rounds):
            self.write_info(f'Running {sync_round} sync round...')

            majority = self.get_nodes_for_syncing()
            if not majority:
                self.write_error('Could not detect nodes majority')
                sys.exit(1)

            to_block_number, majority_nodes = majority
            nodes = {node.identifier: node for node in majority_nodes if node.identifier != my_identifier}
            if not nodes:
                self.write_info('There are no other nodes to sync with in majority other then myself')
                break

            if last_block_number >= to_block_number:
                self.write_info(
                    f'Local blockchain has as many or more blocks as the majority (probably in sync): '
                    f'{last_block_number}'
                )
                break

            self.write_info(f'Syncing to block number: {to_block_number}')
            blocks_to_sync = to_block_number - last_block_number
            node_identifiers = set(nodes.keys())
            while node_identifiers:
                node_identifier = node_identifiers.pop()
                node = nodes[node_identifier]
                self.write_info(f'Syncing from node: {node}')
                block_number = last_block_number
                for block_number, _ in sync_with_node(node, to_block_number):
                    if block_number // 10 == 0:
                        completion_percent = round((block_number - last_block_number) / blocks_to_sync * 100, 2)
                        self.write_success(f'Completed {completion_percent}%')

                completion_percent = round((block_number - last_block_number) / blocks_to_sync * 100, 2)
                self.write_success(f'Completed {completion_percent}%')

                if block_number >= to_block_number:
                    break

            if to_block_number - last_block_number <= tolerable_gap:
                break

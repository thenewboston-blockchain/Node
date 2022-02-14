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

    def sync_from_nodes(self, from_block_number, to_block_number, nodes):
        self.write_info(f'Syncing to block number: {to_block_number}')
        nodes_dict = {node.identifier: node for node in nodes}
        last_block_number = from_block_number - 1
        blocks_to_sync = to_block_number - last_block_number
        node_identifiers = set(nodes_dict.keys())
        while node_identifiers:
            node_identifier = node_identifiers.pop()
            node = nodes_dict[node_identifier]
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

    def handle(self, tolerable_gap, max_sync_rounds, *args, **options):
        my_identifier = get_node_identifier()

        for sync_round in range(max_sync_rounds):
            self.write_info(f'Running {sync_round} sync round...')

            self.write_info('Getting nodes for syncing...')
            nodes = [node for node in get_nodes_for_syncing() if node.identifier != my_identifier]
            if not nodes:
                self.write_info('Nodes for syncing were not found')
                break

            majority = get_nodes_majority(nodes)
            if not majority:
                self.write_error('Majority was not found')
                break

            to_block_number, majority_nodes = majority
            self.write_info(f'Got nodes for syncing (to block number: {to_block_number}):')
            for node in majority_nodes:
                addresses = ', '.join(node.addresses)
                self.write_info(f'- {node.identifier}: {addresses}')

            last_block_number = BlockchainFacade.get_instance().get_next_block_number() - 1
            self.write_info(f'Syncing from block number: {last_block_number + 1}')

            if last_block_number >= to_block_number:
                self.write_info(
                    f'Local blockchain has as many or more blocks as the majority (probably in sync): '
                    f'{last_block_number}'
                )
                break

            gap = to_block_number - last_block_number
            if sync_round > 0 and gap <= tolerable_gap:
                self.write_info(f'Reached tolerable gap of {gap}')
                break

            self.sync_from_nodes(last_block_number + 1, to_block_number, majority_nodes)

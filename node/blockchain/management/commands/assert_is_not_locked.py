import sys

from node.blockchain.utils.lock import delete_lock, is_locked
from node.core.commands import CustomCommand


class Command(CustomCommand):
    help = 'Return non-zero exit code if lock is active'  # noqa: A003

    def add_arguments(self, parser):
        parser.add_argument('name')
        parser.add_argument('-c', '--clear', action='store_true')

    def handle(self, *args, **options):
        name = options['name']
        if is_locked(name):
            self.write_error(f'Lock is active: {name}')
            if options['clear']:
                self.write(f'Clearing lock: {name}')
                delete_lock(name)
                self.write(f'Lock cleared: {name}')

            sys.exit(1)

        self.write_success(f'Lock is not active: {name}')

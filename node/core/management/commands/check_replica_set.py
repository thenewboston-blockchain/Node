import logging
import sys
import time

from node.core.commands import CustomCommand
from node.core.database import is_replica_set_initialized

logger = logging.getLogger(__name__)


class Command(CustomCommand):
    help = 'Check if replica set is initialized'  # noqa: A003

    def add_arguments(self, parser):
        parser.add_argument('-w', '--wait', action='store_true')
        parser.add_argument('-t', '--timeout', type=int, default=60, help='Timeout in seconds')
        parser.add_argument('-p', '--period', type=int, default=1, help='Check period')

    def handle(self, *args, **options):
        expiration = time.time() + options['timeout']
        should_wait = options['wait']
        while True:
            if is_replica_set_initialized():
                self.write_success('Replica set is initialized')
                break

            if should_wait:
                now = time.time()
                if now < expiration:
                    self.write(f'Replica set is not initialized yet, waiting (ts: {now})..')
                    time.sleep(1)
                else:
                    self.write_error('Timed out')
                    sys.exit(1)
            else:
                self.write_error('Replica set is not initialized')
                sys.exit(1)

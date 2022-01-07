import sys

from django.core.management import BaseCommand

from node.blockchain.utils.lock import is_locked


class Command(BaseCommand):
    help = 'Return non-zero exit code if lock is active'  # noqa: A003

    def add_arguments(self, parser):
        parser.add_argument('name')

    def handle(self, *args, **options):
        if is_locked(options['name']):
            sys.exit(1)

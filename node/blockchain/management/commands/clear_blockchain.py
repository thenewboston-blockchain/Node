import logging

from django.core.management.base import BaseCommand

from node.blockchain.facade import BlockchainFacade
from node.blockchain.utils.lock import delete_all_locks

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Clears local blockchain'  # noqa: A003
    output_transaction = True

    def handle(self, *args, **options):
        delete_all_locks()
        BlockchainFacade.get_instance().clear()

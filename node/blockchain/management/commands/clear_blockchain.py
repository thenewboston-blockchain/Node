import logging

from django.core.management.base import BaseCommand

from node.blockchain.facade import BlockchainFacade

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Clears local blockchain'  # noqa: A003
    output_transaction = True

    def handle(self, *args, **options):
        BlockchainFacade.get_instance().clear()

import logging

from celery import shared_task

from node.blockchain.facade import BlockchainFacade
from node.blockchain.models import PendingBlock

logger = logging.getLogger(__name__)


def validate_pending_block(orm_pending_block: PendingBlock):
    pending_block = orm_pending_block.get_block()
    return pending_block


def process_next_block() -> bool:
    # TODO(dmu) CRITICAL: Process pending blocks. To be implemented in
    #                     https://thenewboston.atlassian.net/browse/BC-263
    facade = BlockchainFacade.get_instance()
    next_block_number = facade.get_next_block_number()

    # There may be more than one pending block, but at most one of them can be valid
    orm_pending_blocks = list(PendingBlock.objects.filter(number=next_block_number))
    for orm_pending_block in orm_pending_blocks:
        try:
            validate_pending_block(orm_pending_block)
            return False
        except Exception:
            logger.warning('Error while trying to validate pending block: %s', orm_pending_block, exc_info=True)

    return False


@shared_task
def process_pending_blocks_task():
    should_process_next_block = True
    while should_process_next_block:
        should_process_next_block = process_next_block()


def start_process_pending_blocks_task():
    process_pending_blocks_task.delay()

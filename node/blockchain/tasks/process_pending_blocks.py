import logging
from typing import Optional

from celery import shared_task
from pydantic.error_wrappers import ValidationError as PydanticValidationError

from node.blockchain.constants import BLOCK_LOCK
from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import Block as PydanticBlock
from node.blockchain.inner_models import BlockConfirmation as PydanticBlockConfirmation
from node.blockchain.models import BlockConfirmation, PendingBlock
from node.blockchain.utils.lock import lock
from node.core.exceptions import ValidationError
from node.core.utils.cryptography import get_signing_key

from .process_block_confirmations import start_process_block_confirmations_task

logger = logging.getLogger(__name__)


@lock(BLOCK_LOCK)
def lock_and_validate(pending_block) -> Optional[PydanticBlock]:
    try:
        block = pending_block.get_block()
        block.validate_all(BlockchainFacade.get_instance())
    except (PydanticValidationError, ValidationError):
        logger.warning('Block did not pass validation: %s', pending_block, exc_info=True)
        return None

    return block


def process_block(block_number) -> bool:
    orm_block_confirmation = BlockConfirmation.objects.get_or_none(number=block_number, signer=get_signing_key())
    if orm_block_confirmation:
        logger.warning('Block %s is already confirmed')
        return False  # block is already confirmed

    primary_validator = BlockchainFacade.get_instance().get_primary_validator()
    assert primary_validator is not None
    pending_block = PendingBlock.objects.get_or_none(number=block_number, signer=primary_validator.identifier)
    if not pending_block:
        logger.warning('Pending block for block number %s could not be found')
        return False

    if not (block := lock_and_validate(pending_block)):
        logger.warning('Block %s is not valid')
        return False

    block_confirmation = PydanticBlockConfirmation.create_from_block(block, get_signing_key())
    BlockConfirmation.objects.update_or_create_from_block_confirmation(block_confirmation)
    start_process_block_confirmations_task()
    # TODO(dmu) CRITICAL: Send out the confirmation to other CVs
    #                     https://thenewboston.atlassian.net/browse/BC-291
    return True


@shared_task
def process_pending_blocks_task():
    next_block_number = BlockchainFacade.get_instance().get_next_block_number()
    while True:
        # This implementation is safer in terms of infinitive loops
        if not process_block(next_block_number):
            break
        next_block_number += 1


def start_process_pending_blocks_task():
    process_pending_blocks_task.delay()

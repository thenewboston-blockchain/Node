import logging

from celery import shared_task
from pydantic.error_wrappers import ValidationError as PydanticValidationError

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import BlockConfirmation as PydanticBlockConfirmation
from node.blockchain.models import BlockConfirmation, PendingBlock
from node.core.exceptions import ValidationError
from node.core.utils.cryptography import get_signing_key

logger = logging.getLogger(__name__)


def process_next_block() -> bool:
    facade = BlockchainFacade.get_instance()
    primary_validator = facade.get_primary_validator()
    assert primary_validator is not None
    next_block_number = facade.get_next_block_number()

    pending_block = PendingBlock.objects.get_or_none(number=next_block_number, signer=primary_validator.identifier)
    if not pending_block:
        return False

    try:
        block = pending_block.get_block()
        block.validate_all(facade)
    except (PydanticValidationError, ValidationError):
        logger.warning('Block did not pass validation: %s', pending_block, exc_info=True)
        return False

    block_confirmation = PydanticBlockConfirmation.create_from_block(block, get_signing_key())
    BlockConfirmation.objects.update_or_create_from_block_confirmation(block_confirmation)
    # TODO(dmu) CRITICAL: Process pending blocks. To be implemented in
    #                     https://thenewboston.atlassian.net/browse/BC-263
    # Send out the confirmation to other CVs
    # Test that block with invalid signature is not accepted
    return True


@shared_task
def process_pending_blocks_task():
    should_process_next_block = True
    while should_process_next_block:
        should_process_next_block = process_next_block()


def start_process_pending_blocks_task():
    process_pending_blocks_task.delay()

import logging
from itertools import groupby
from operator import attrgetter

from celery import shared_task
from django.db import transaction

from node.blockchain.constants import BLOCK_LOCK
from node.blockchain.facade import BlockchainFacade
from node.blockchain.models import BlockConfirmation, PendingBlock
from node.blockchain.utils.lock import lock
from node.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


@lock(BLOCK_LOCK)
def process_next_block():
    facade = BlockchainFacade.get_instance()
    next_block_number = facade.get_next_block_number()
    cv_identifiers = facade.get_confirmation_validator_identifiers()

    # Query only confirmations for the next block number and received from confirmation validators
    all_confirmations = BlockConfirmation.objects.filter(number=next_block_number, signer__in=cv_identifiers)

    # Group confirmations by hash to see which hash wins the consensus
    grouped_confirmations = groupby(all_confirmations.order_by('hash'), key=attrgetter('hash'))
    minimum_consensus = facade.get_minimum_consensus()

    finalizable_hashes = [(hash_, confirmations)
                          for hash_, confirmations in grouped_confirmations
                          if len(list(confirmations)) >= minimum_consensus]

    if not finalizable_hashes:
        return False  # No consensus, yet

    if len(finalizable_hashes) >= 2:
        # We should never get here
        raise ValueError('More than one finalizable hash found')

    assert len(finalizable_hashes) == 1
    hash_, consensus_confirmations = finalizable_hashes[0]

    # Validate confirmations, since they may have not been validated on API call because some of them were added
    # much earlier then the next block number become equal to confirmation block number
    valid_confirmations = []
    for confirmation in consensus_confirmations:
        try:
            confirmation.validate_all()
        except ValidationError:
            logger.warning('Invalid confirmation detected: %s', confirmation)
            continue

        valid_confirmations.append(confirmation)

    if len(valid_confirmations) < minimum_consensus:  # Check that we still have consensus after validation
        return False

    pending_block = PendingBlock.objects.get_or_none(number=next_block_number, hash=hash_)
    if pending_block is None:
        # TODO(dmu) CRITICAL: https://thenewboston.atlassian.net/browse/BC-283
        raise NotImplementedError('Edge case of processing confirmed missing pending block is not implemented')

    with transaction.atomic():
        facade.add_block_from_json(pending_block.body, expect_locked=True)
        # There may be blocks with other hashes therefore we delete all of them
        PendingBlock.objects.filter(number__lte=next_block_number).delete()
        BlockConfirmation.objects.filter(number__lte=next_block_number).delete()

    return True


@shared_task
def process_block_confirmations_task():
    should_process_next_block = True
    while should_process_next_block:
        should_process_next_block = process_next_block()


def start_process_block_confirmations_task():
    process_block_confirmations_task.delay()

import logging
from itertools import groupby
from operator import attrgetter
from typing import Optional

from celery import shared_task
from django.db import transaction

from node.blockchain.constants import BLOCK_LOCK
from node.blockchain.facade import BlockchainFacade
from node.blockchain.mixins.crypto import HashableStringWrapper
from node.blockchain.models import BlockConfirmation, PendingBlock
from node.blockchain.types import Hash
from node.blockchain.utils.lock import lock
from node.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


def get_next_block_confirmations(next_block_number) -> list[BlockConfirmation]:
    cv_identifiers = BlockchainFacade.get_instance().get_confirmation_validator_identifiers()
    return list(BlockConfirmation.objects.filter(number=next_block_number, signer__in=cv_identifiers))


def get_consensus_block_hash_with_confirmations(
    confirmations: list[BlockConfirmation], minimum_consensus: int
) -> Optional[tuple[Hash, list[BlockConfirmation]]]:

    assert len(set(confirmation.number for confirmation in confirmations)) <= 1

    key_func = attrgetter('hash')
    grouped_confirmations = [(Hash(hash_), list(confirmations_))
                             for hash_, confirmations_ in groupby(sorted(confirmations, key=key_func), key=key_func)]
    finalizable_hashes = [(hash_, confirmations_)
                          for hash_, confirmations_ in grouped_confirmations
                          if len(confirmations_) >= minimum_consensus]

    if not finalizable_hashes:
        return None  # No consensus, yet

    if len(finalizable_hashes) >= 2:
        raise ValueError('More than one finalizable hash found')  # We should never get here

    assert len(finalizable_hashes) == 1
    block_hash, consensus_confirmations = finalizable_hashes[0]
    assert len(set(confirmation.signer for confirmation in consensus_confirmations)) == len(consensus_confirmations)
    return block_hash, consensus_confirmations


def is_valid_consensus(confirmations: list[BlockConfirmation], minimum_consensus: int):
    # Validate confirmations, since they may have not been validated on API call because some of them were added
    # much earlier then the next block number become equal to confirmation block number
    assert len(set(confirmation.number for confirmation in confirmations)) <= 1
    assert len(set(confirmation.hash for confirmation in confirmations)) <= 1
    assert len(set(confirmation.signer for confirmation in confirmations)) == len(confirmations)
    facade = BlockchainFacade.get_instance()

    confirmations_left = minimum_consensus
    for confirmation in confirmations:
        try:
            confirmation.get_block_confirmation().validate_all(facade)
        except ValidationError:
            logger.warning('Invalid confirmation detected: %s', confirmation)
            continue

        confirmations_left -= 1
        if confirmations_left <= 0:
            return True

    return False


@lock(BLOCK_LOCK)
def process_next_block():
    facade = BlockchainFacade.get_instance()
    next_block_number = facade.get_next_block_number()
    confirmations = get_next_block_confirmations(next_block_number)

    minimum_consensus = facade.get_minimum_consensus()
    if not (result := get_consensus_block_hash_with_confirmations(confirmations, minimum_consensus)):
        return False

    block_hash, confirmations = result
    if not is_valid_consensus(confirmations, minimum_consensus):
        return False

    pending_block = PendingBlock.objects.get_or_none(number=next_block_number, hash=block_hash)
    if pending_block is None:
        # TODO(dmu) CRITICAL: https://thenewboston.atlassian.net/browse/BC-283
        raise NotImplementedError('Edge case of processing confirmed missing pending block is not implemented')

    block_body = pending_block.body
    if HashableStringWrapper(block_body).make_hash() != block_hash:
        raise ValidationError('Pending block body hash is not valid')  # we should never get here

    with transaction.atomic():
        facade.add_block_from_json(block_body, expect_locked=True)
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

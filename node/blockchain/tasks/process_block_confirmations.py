from itertools import groupby
from operator import attrgetter

from celery import shared_task
from django.db import transaction

from node.blockchain.constants import BLOCK_LOCK
from node.blockchain.facade import BlockchainFacade
from node.blockchain.models import BlockConfirmation, PendingBlock
from node.blockchain.utils.lock import lock


@lock(BLOCK_LOCK)
def process_next_block():
    facade = BlockchainFacade.get_instance()
    next_block_number = facade.get_next_block_number()
    cv_identifiers = facade.get_confirmation_validator_identifiers()
    confirmations = BlockConfirmation.objects.filter(number=next_block_number, signer__in=cv_identifiers)
    grouped_confirmations = groupby(confirmations.order_by('hash'), key=attrgetter('hash'))
    minimum_consensus = len(cv_identifiers) * 2 / 3

    finalizable_hashes = [
        hash_ for hash_, _confirmations in grouped_confirmations if len(list(_confirmations)) >= minimum_consensus
    ]

    if not finalizable_hashes:
        return False

    if len(finalizable_hashes) >= 2:
        # We should never get here
        raise ValueError('More than one finalizable hash found')

    assert len(finalizable_hashes) == 1
    hash_ = finalizable_hashes[0]

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

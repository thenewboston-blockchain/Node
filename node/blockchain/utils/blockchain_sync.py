import logging
from typing import Optional

from django.db import transaction

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import Block
from node.core.clients.node import NodeClient
from node.core.database import is_in_transaction
from node.core.exceptions import BlockchainSyncError

logger = logging.getLogger(__name__)


def get_default_to_block_number(address, to_block_number) -> int:
    if to_block_number is not None:
        return to_block_number

    last_block_number = NodeClient.get_instance().get_last_block_number(address)
    if last_block_number is None:
        raise BlockchainSyncError('Could not get last block number from %s', address)

    return last_block_number


def sync_with_address(address: str, to_block_number: Optional[int] = None):
    facade = BlockchainFacade.get_instance()
    start_block_number = facade.get_next_block_number()
    to_block_number = get_default_to_block_number(address, to_block_number)
    blocks_to_sync = to_block_number - start_block_number + 1

    # It is OK to have `by_limit` higher than max pagination limit, the API will just get the minimum of two
    block_generator = NodeClient.get_instance().yield_blocks_dict(
        address, block_number_min=start_block_number, block_number_max=to_block_number
    )
    for block in block_generator:
        try:
            block_obj = Block.parse_obj(block)
            block_number = block_obj.get_block_number()
            if block_number < start_block_number:
                logger.warning(
                    'Got block number %s from node when expected %s, skipping', block_number, start_block_number
                )
                continue

            if block_number > to_block_number:
                logger.warning(
                    'Got block number %s from node when expected %s, skipping', block_number, start_block_number
                )
                break

            if is_in_transaction():
                facade.add_block(block_obj)
            else:
                with transaction.atomic():
                    facade.add_block(block_obj)
            logger.debug('Synced block number %s', block_number)
        except Exception as ex:
            raise BlockchainSyncError('Could not add block: %s', block) from ex

        yield block_number, (block_number - start_block_number + 1) / blocks_to_sync


def sync_with_node(node, to_block_number: Optional[int] = None):
    address = NodeClient.get_instance().get_node_online_address(node)
    if address is None:
        raise BlockchainSyncError('Node %s is not available', node)

    to_block_number = get_default_to_block_number(address, to_block_number)
    yield from sync_with_address(address, to_block_number=to_block_number)

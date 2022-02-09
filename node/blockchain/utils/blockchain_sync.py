import logging
from typing import Optional

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import Block
from node.core.clients.node import NodeClient
from node.core.exceptions import BlockchainSyncError

logger = logging.getLogger(__name__)


def set_default_from_block_number(from_block_number):
    return BlockchainFacade.get_instance().get_next_block_number() if from_block_number is None else from_block_number


def set_default_to_block_number(address, to_block_number):
    if to_block_number is not None:
        return to_block_number

    last_block_number = NodeClient.get_instance().get_last_block_number(address)
    if last_block_number is None:
        raise BlockchainSyncError('Could not get last block number from %s', address)

    return last_block_number


def sync_with_address(address: str, from_block_number: Optional[int] = None, to_block_number: Optional[int] = None):
    from_block_number = set_default_from_block_number(from_block_number)
    to_block_number = set_default_to_block_number(address, to_block_number)

    client = NodeClient.get_instance()
    facade = BlockchainFacade.get_instance()
    next_block_number = from_block_number

    # It is OK to have `by_limit` higher than max pagination limit, the API will just get the minimum of two
    block_generator = client.yield_blocks_raw(
        address, block_number_min=next_block_number, block_number_max=to_block_number
    )
    for block in block_generator:
        try:
            block_obj = Block.parse_obj(block)
            block_number = block_obj.get_block_number()
            if block_number < next_block_number:
                logger.warning(
                    'Got block number %s from node when expected %s, skipping', block_number, next_block_number
                )
                continue

            if block_number > to_block_number:
                logger.warning(
                    'Got block number %s from node when expected %s, skipping', block_number, next_block_number
                )
                break

            facade.add_block(block_obj)
        except Exception as ex:
            raise BlockchainSyncError('Could not add block: %s', block) from ex


def sync_with_node(node, from_block_number: Optional[int] = None, to_block_number: Optional[int] = None):
    # TODO(dmu) CRITICAL: Wrap in transaction
    #                     https://thenewboston.atlassian.net/browse/BC-189
    client = NodeClient.get_instance()
    address = client.get_node_online_address(node)
    if address is None:
        raise BlockchainSyncError('Node %s is not available', node)

    from_block_number = set_default_from_block_number(from_block_number)
    to_block_number = set_default_to_block_number(address, to_block_number)

    sync_generator = sync_with_address(address, from_block_number=from_block_number, to_block_number=to_block_number)
    for block_number in sync_generator:
        assert from_block_number >= block_number >= to_block_number
        yield block_number

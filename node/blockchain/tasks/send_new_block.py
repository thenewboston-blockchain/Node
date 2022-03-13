import logging

from celery import shared_task

from node.blockchain.facade import BlockchainFacade
from node.blockchain.models.block import Block as ORMBlock
from node.blockchain.types import NodeRole
from node.core.clients.node import NodeClient

logger = logging.getLogger(__name__)


@shared_task
def send_new_block_to_node_task(block_number, node_identifier):
    node = BlockchainFacade.get_instance().get_node_by_identifier(node_identifier)
    block = ORMBlock.objects.get_block_by_number(block_number)
    NodeClient.get_instance().send_block(node, block.body)


@shared_task
def send_new_block_task(block_number):
    logger.debug('Sending block number %s to all CVs', block_number)
    for node in BlockchainFacade.get_instance().yield_nodes(roles={NodeRole.CONFIRMATION_VALIDATOR}):
        logger.debug('Sending block number %s to %s', block_number, node)
        send_new_block_to_node_task.delay(block_number, node.identifier)


def start_send_new_block_task(block_number):
    send_new_block_task.delay(block_number)

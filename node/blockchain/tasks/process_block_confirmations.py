from celery import shared_task

# from node.blockchain.facade import BlockchainFacade


@shared_task
def process_block_confirmations_task():
    # TODO(dmu) CRITICAL: Implement https://thenewboston.atlassian.net/browse/BC-272
    # facade = BlockchainFacade.get_instance()
    # next_block_number = facade.get_next_block_number()
    # get all confirmation for next block number
    # if there is no 2/3
    raise NotImplementedError


def start_process_block_confirmations_task():
    process_block_confirmations_task.delay()

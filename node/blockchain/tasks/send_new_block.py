from celery import shared_task


@shared_task
def send_new_block_to_node_task():
    raise NotImplementedError


@shared_task
def send_new_block_task(block_number):
    raise NotImplementedError


def start_send_new_block_task():
    send_new_block_task.delay()

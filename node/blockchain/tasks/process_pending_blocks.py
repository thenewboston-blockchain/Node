from celery import shared_task


@shared_task(bind=True)
def process_pending_blocks_task(self):
    # TODO(dmu) CRITICAL: Process pending blocks. To be implemented in
    #                     https://thenewboston.atlassian.net/browse/BC-263
    pass


def start_process_pending_blocks_task():
    process_pending_blocks_task.delay()

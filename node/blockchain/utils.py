import functools
from contextlib import ContextDecorator

from node.core.exceptions import BlockchainLockedError


def ensure_locked(name):

    def decorator(func):

        @functools.wraps(func)
        def wrap(self, *args, **kwargs):
            expect_locked = kwargs.pop('expect_locked', False)

            from node.blockchain.models import Lock
            if Lock.objects.filter(name=name).exists() is not expect_locked:
                raise BlockchainLockedError(
                    'Locked status is not as expected. Probably it is being modified by another process'
                )

            if expect_locked is True:
                return func(self, *args, **kwargs)

            with TableLocker(name):
                return func(self, *args, **kwargs)

        return wrap

    return decorator


class TableLocker(ContextDecorator):

    def __init__(self, name):
        self.name = name
        self.lock = None

    def __enter__(self):
        from node.blockchain.models import Lock
        self.lock, is_created = Lock.objects.get_or_create(name=self.name)
        if not is_created:
            raise BlockchainLockedError('Blockchain locked. Probably it is being modified by another process')

    def __exit__(self, exc_type, exc_val, exc_tb):
        deleted, _ = self.lock.delete()
        if deleted == 0:
            raise BlockchainLockedError('Blockchain lock object was unexpected deleted.')

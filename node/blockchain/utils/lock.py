import functools

from node.core.exceptions import BlockchainIsNotLockedError, BlockchainLockingError, BlockchainUnlockingError


def lock(name):

    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            expect_locked = kwargs.pop('expect_locked', False)

            from node.blockchain.models import Lock

            if expect_locked:
                is_already_locked = Lock.objects.filter(_id=name).exists()
                if not is_already_locked:
                    raise BlockchainIsNotLockedError

                return func(*args, **kwargs)

            lock_obj, is_created = Lock.objects.get_or_create(_id=name)
            is_already_locked = not is_created

            if is_already_locked:
                raise BlockchainLockingError

            return_value = func(*args, **kwargs)
            delete_count, _ = lock_obj.delete()
            if delete_count < 1:
                raise BlockchainUnlockingError

            return return_value

        return wrapper

    return decorator

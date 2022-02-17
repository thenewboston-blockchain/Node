import functools

from pymongo.errors import DuplicateKeyError

from node.core.database import get_database
from node.core.exceptions import BlockchainIsNotLockedError, BlockchainLockingError, BlockchainUnlockingError


def get_lock_collection():
    return get_database().lock


def make_filter(name):
    return {'_id': name}


def is_locked(name):
    return bool(get_lock_collection().find_one(make_filter(name)))


def create_lock(name):
    get_lock_collection().insert_one(make_filter(name))


def delete_lock(name):
    return get_lock_collection().delete_one(make_filter(name))


def delete_all_locks():
    return get_lock_collection().remove()


def lock(name, expect_locked=False):
    outer_expect_locked = expect_locked

    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            bypass_lock_validation = kwargs.pop('bypass_lock_validation', False)
            if bypass_lock_validation:
                return func(*args, **kwargs)

            inner_expect_locked = kwargs.pop('expect_locked', outer_expect_locked)

            if inner_expect_locked:
                is_already_locked = is_locked(name)
                if not is_already_locked:
                    raise BlockchainIsNotLockedError

                return func(*args, **kwargs)

            try:
                create_lock(name)
            except DuplicateKeyError:
                raise BlockchainLockingError

            return_value = func(*args, **kwargs)
            delete_result = delete_lock(name)

            if delete_result.deleted_count < 1:
                raise BlockchainUnlockingError

            return return_value

        return wrapper

    return decorator

import functools
import logging
import time
from typing import Optional

from django.conf import settings
from django.db import transaction
from pymongo.errors import DuplicateKeyError

from node.core.database import get_database
from node.core.exceptions import BlockchainIsNotLockedError, BlockchainLockingError, BlockchainUnlockingError

logger = logging.getLogger(__name__)


def get_lock_collection():
    return get_database().lock


def make_filter(name):
    return {'_id': name}


def is_locked(name):
    return bool(get_lock_collection().find_one(make_filter(name)))


def insert_lock(name):
    get_lock_collection().insert_one(make_filter(name))


def create_lock(name, timeout_seconds: Optional[float] = None):
    # TODO(dmu) HIGH: Make sure that timeout works correctly in conjunction with async behavior (Daphne)
    #                 https://thenewboston.atlassian.net/browse/BC-258
    if timeout_seconds is None:  # shortcut
        try:
            insert_lock(name)
        except DuplicateKeyError:
            raise BlockchainLockingError('Lock could not be acquired: %s', name)

        return

    sleep_seconds = timeout_seconds / 10
    timeout_moment = time.time() + timeout_seconds
    while True:
        if not is_locked(name):
            try:
                insert_lock(name)
                return
            except DuplicateKeyError:
                logger.warning('Could not manage to get the lock :(')

        logger.debug('Waiting to acquire lock: %s', name)
        time.sleep(sleep_seconds)

        if time.time() >= timeout_moment:  # this makes sure we have at least one iteration
            break

    raise BlockchainLockingError('Blockchain locking timeout for lock: %s', name)


def delete_lock(name):
    logger.debug('Deleting lock: %s', name)
    result = get_lock_collection().delete_one(make_filter(name))
    if result.deleted_count < 1:
        logger.warning('Lock %s was not found', name)
    else:
        logger.debug('Deleted lock: %s', name)
    return result


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
                create_lock(name, timeout_seconds=settings.LOCK_DEFAULT_TIMEOUT_SECONDS)
                transaction.get_connection().on_rollback(lambda: delete_lock(name))
            except DuplicateKeyError:
                raise BlockchainLockingError

            return_value = func(*args, **kwargs)
            delete_result = delete_lock(name)

            if delete_result.deleted_count < 1:
                raise BlockchainUnlockingError

            return return_value

        return wrapper

    return decorator

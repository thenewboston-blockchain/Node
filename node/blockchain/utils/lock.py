import functools
import threading

from django.conf import settings
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from node.core.exceptions import BlockchainIsNotLockedError, BlockchainLockingError, BlockchainUnlockingError

thread_storage = threading.local()
thread_storage.pymongo_client = None


def get_pymongo_client():
    if (client := thread_storage.pymongo_client) is None:
        client_settings = settings.DATABASES['default']['CLIENT']
        thread_storage.pymongo_client = client = MongoClient(**client_settings)

    return client


def get_database():
    return get_pymongo_client()[settings.DATABASES['default']['NAME']]


def create_lock(name):
    get_database().lock.insert_one({'_id': name})


def delete_lock(name):
    return get_database().lock.delete_one({'_id': name})


def lock(name):

    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            expect_locked = kwargs.pop('expect_locked', False)

            lock_collection = get_database().lock
            filter_ = {'_id': name}
            if expect_locked:
                is_already_locked = bool(lock_collection.find_one(filter_))
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

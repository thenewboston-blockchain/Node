import functools
import threading

from django.conf import settings
from django.db import transaction
from pymongo import MongoClient
from pymongo.errors import OperationFailure

from node.core.exceptions import DatabaseTransactionError

thread_storage = threading.local()


def is_in_transaction():
    return (connection := transaction.get_connection()) and connection.in_atomic_block


def ensure_in_transaction(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not is_in_transaction():
            raise DatabaseTransactionError('Expected to have an active transaction')

        return func(*args, **kwargs)

    return wrapper


def get_pymongo_client():
    if (client := getattr(thread_storage, 'pymongo_client', None)) is None:
        client_settings = settings.DATABASES['default']['CLIENT']
        thread_storage.pymongo_client = client = MongoClient(**client_settings)

    return client


def get_database():
    return get_pymongo_client()[settings.DATABASES['default']['NAME']]


def is_replica_set_initialized():
    client = get_pymongo_client()
    try:
        result = client.admin.command({'replSetGetStatus': 1})
    except OperationFailure as ex:
        details = ex.details
        if details.get('code') == 94 or details.get('codeName') == 'NotYetInitialized':
            return False

        raise

    return result.get('ok') == 1

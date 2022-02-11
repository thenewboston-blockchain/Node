import functools

from django.db import transaction

from node.core.exceptions import DatabaseTransactionError


def is_in_transaction():
    return (connection := transaction.get_connection()) and connection.in_atomic_block


def ensure_in_transaction(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not is_in_transaction():
            raise DatabaseTransactionError('Expected to have an active transaction')

        return func(*args, **kwargs)

    return wrapper

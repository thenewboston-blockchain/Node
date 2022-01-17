import functools

from django.db import transaction

from node.core.exceptions import TransactionError


def ensure_in_transaction(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not ((connection := transaction.get_connection()) and connection.in_atomic_block):
            raise TransactionError('Expected to have an active transaction')

        return func(*args, **kwargs)

    return wrapper

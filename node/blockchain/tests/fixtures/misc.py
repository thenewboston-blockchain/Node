import pytest
from django.test import override_settings

from node.core.database import get_database


@pytest.fixture
def treasury_amount():
    return 281474976710656


@pytest.fixture
def lock_collection():
    return get_database().lock


@pytest.fixture(autouse=True)
def clean_up_mylock(lock_collection):
    lock_collection.delete_one({'_id': 'mylock'})
    yield
    lock_collection.delete_one({'_id': 'mylock'})


@pytest.fixture(autouse=True)
def clean_up_block_lock(lock_collection):
    lock_collection.delete_one({'_id': 'block'})
    yield
    lock_collection.delete_one({'_id': 'block'})


@pytest.fixture(autouse=True)
def quick_lock_timeout():
    with override_settings(LOCK_DEFAULT_TIMEOUT_SECONDS=0.001):
        yield

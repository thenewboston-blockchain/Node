import pytest

from node.blockchain.utils.lock import get_database


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

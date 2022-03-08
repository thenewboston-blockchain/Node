import pytest
from django.test import override_settings

from node.core.database import get_database


@pytest.fixture(autouse=True)
def set_common_signing_key(settings):
    settings.SECRET_KEY = 'b27c612c6cbeac10c8788fbc95b29f563cc0ea2eb7d6be08' \
                          '684f565b6884f6f60a59ec73d10db0f9bbd2cd7bfaa0af28'
    settings.NODE_SIGNING_KEY = 'a025da120a1c95b27f17bb9442af9c27d3a357733aa150b458f21682a2d539a9'


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

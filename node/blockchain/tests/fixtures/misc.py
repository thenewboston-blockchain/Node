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
def test_settings(settings):
    with override_settings(
        USE_ON_COMMIT_HOOK=False,
        LOCK_DEFAULT_TIMEOUT_SECONDS=0.001,
        SECRET_KEY='b27c612c6cbeac10c8788fbc95b29f563cc0ea2eb7d6be08',
        NODE_SIGNING_KEY='a025da120a1c95b27f17bb9442af9c27d3a357733aa150b458f21682a2d539a9',
        CELERY_BROKER_URL='memory://',
        CELERY_TASK_ALWAYS_EAGER=True,
    ):
        yield

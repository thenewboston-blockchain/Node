import time

import pytest
from django.conf import settings
from pymongo import MongoClient

from node.blockchain.utils.lock import create_lock, lock
from node.core.database import get_database
from node.core.exceptions import BlockchainIsNotLockedError, BlockchainLockingError, BlockchainUnlockingError


def has_lock(name):
    client_settings = settings.DATABASES['default']['CLIENT']
    client = MongoClient(**client_settings)
    return bool(client[settings.DATABASES['default']['NAME']].lock.find_one({'_id': name}))


@pytest.mark.django_db
def test_setting_lock():
    assert not has_lock('mylock')

    @lock('mylock')
    def locked_function():
        assert has_lock('mylock')

    locked_function()

    assert not has_lock('mylock')


@pytest.mark.django_db
def test_setting_lock_if_already_locked():
    assert not has_lock('mylock')

    @lock('mylock')
    def locked_function():
        assert has_lock('mylock')

    @lock('mylock')
    def lock_and_call():
        assert has_lock('mylock')
        with pytest.raises(BlockchainLockingError, match='Blockchain locking timeout for lock'):
            locked_function()

        raise BlockchainLockingError  # prevent exception swallowing by pytest.raises()

    with pytest.raises(BlockchainLockingError):
        lock_and_call()
        assert has_lock('mylock')


@pytest.mark.django_db
def test_unlocking_if_already_unlocked():
    assert not has_lock('mylock')

    @lock('mylock')
    def locked_function():
        assert has_lock('mylock')
        get_database().lock.delete_one({'_id': 'mylock'})

    with pytest.raises(BlockchainUnlockingError):
        locked_function()


@pytest.mark.django_db
def test_ensure_locked():
    assert not has_lock('mylock')

    @lock('mylock')
    def expect_locked_function():
        assert has_lock('mylock')

    @lock('mylock')
    def locked_function():
        assert has_lock('mylock')
        expect_locked_function(expect_locked=True)

    locked_function()

    assert not has_lock('mylock')


@pytest.mark.django_db
def test_ensure_locked_if_not_locked():
    assert not has_lock('mylock')

    @lock('mylock')
    def expect_locked_function():
        assert has_lock('mylock')

    with pytest.raises(BlockchainIsNotLockedError):
        expect_locked_function(expect_locked=True)

    assert not has_lock('mylock')


@pytest.mark.django_db
def test_cannot_create_lock_twice():
    create_lock('mylock')
    with pytest.raises(BlockchainLockingError, match='Lock could not be acquired'):
        create_lock('mylock')


@pytest.mark.django_db
def test_cannot_create_lock_twice_with_longer_timeout():
    create_lock('mylock')
    start = time.time()
    with pytest.raises(BlockchainLockingError, match='Blockchain locking timeout for lock'):
        create_lock('mylock', timeout_seconds=0.1)

    end = time.time()
    assert 0.1 <= end - start <= 0.2

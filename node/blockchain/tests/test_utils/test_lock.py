import pytest
from django.conf import settings
from pymongo import MongoClient

from node.blockchain.utils.lock import get_database, lock
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
        with pytest.raises(BlockchainLockingError):
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

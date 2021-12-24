import pytest

from node.blockchain.models import Lock
from node.blockchain.utils.lock import lock
from node.core.exceptions import BlockchainIsNotLockedError, BlockchainLockingError, BlockchainUnlockingError


@pytest.mark.django_db
def test_setting_lock():
    assert not Lock.objects.filter(_id='mylock').exists()

    @lock('mylock')
    def locked_function():
        assert Lock.objects.filter(_id='mylock').exists()

    locked_function()

    assert not Lock.objects.filter(_id='mylock').exists()


@pytest.mark.django_db
def test_setting_lock_if_already_locked():
    assert not Lock.objects.filter(_id='mylock').exists()

    @lock('mylock')
    def locked_function():
        assert Lock.objects.filter(_id='mylock').exists()

    @lock('mylock')
    def lock_and_call():
        assert Lock.objects.filter(_id='mylock').exists()
        with pytest.raises(BlockchainLockingError):
            locked_function()

        raise BlockchainLockingError  # prevent exception swallowing by pytest.raises()

    with pytest.raises(BlockchainLockingError):
        lock_and_call()
        assert Lock.objects.filter(_id='mylock').exists()


@pytest.mark.django_db
def test_unlocking_if_already_unlocked():
    assert not Lock.objects.filter(_id='mylock').exists()

    @lock('mylock')
    def locked_function():
        assert Lock.objects.filter(_id='mylock').exists()
        Lock.objects.filter(_id='mylock').delete()

    with pytest.raises(BlockchainUnlockingError):
        locked_function()


@pytest.mark.django_db
def test_ensure_locked():
    assert not Lock.objects.filter(_id='mylock').exists()

    @lock('mylock')
    def expect_locked_function():
        assert Lock.objects.filter(_id='mylock').exists()

    @lock('mylock')
    def locked_function():
        assert Lock.objects.filter(_id='mylock').exists()
        expect_locked_function(expect_locked=True)

    locked_function()

    assert not Lock.objects.filter(_id='mylock').exists()


@pytest.mark.django_db
def test_ensure_locked_if_not_locked():
    assert not Lock.objects.filter(_id='mylock').exists()

    @lock('mylock')
    def expect_locked_function():
        assert Lock.objects.filter(_id='mylock').exists()

    with pytest.raises(BlockchainIsNotLockedError):
        expect_locked_function(expect_locked=True)

    assert not Lock.objects.filter(_id='mylock').exists()

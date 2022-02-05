import pytest
from django.db import transaction

from node.blockchain.models.account_state import AccountState
from node.core.database import ensure_in_transaction
from node.core.exceptions import DatabaseTransactionError


@pytest.mark.django_db
@pytest.mark.parametrize('iteration', map(str, range(3)))  # we need multiple iteration for proper testing
def test_create_object_in_database(iteration):
    assert not AccountState.objects.exists()
    account_state = AccountState.objects.create(account_lock='0' * 64)
    assert AccountState.objects.exists()
    assert AccountState.objects.count() == 1
    db_account_state = AccountState.objects.first()
    assert db_account_state
    assert db_account_state._id == account_state._id


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures('cleanup_for_rollback_and_commit_tests')
def test_rollback():

    class TestError(Exception):
        pass

    try:
        with transaction.atomic():
            assert not AccountState.objects.exists()
            account_state = AccountState.objects.create(account_lock='0' * 64)
            assert AccountState.objects.exists()
            assert AccountState.objects.count() == 1
            db_account_state = AccountState.objects.first()
            assert db_account_state
            assert db_account_state._id == account_state._id

            raise TestError
    except TestError:
        assert not AccountState.objects.exists()


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures('cleanup_for_rollback_and_commit_tests')
def test_commit():
    with transaction.atomic():
        assert not AccountState.objects.exists()
        account_state = AccountState.objects.create(account_lock='0' * 64)

    assert AccountState.objects.exists()
    assert AccountState.objects.count() == 1
    db_account_state = AccountState.objects.first()
    assert db_account_state
    assert db_account_state._id == account_state._id


def test_ensure_in_transaction():

    @ensure_in_transaction
    def test_me():
        pass

    with pytest.raises(DatabaseTransactionError, match='Expected to have an active transaction'):
        test_me()

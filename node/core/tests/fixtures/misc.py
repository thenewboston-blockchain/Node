import pytest
from django.db import transaction

from node.blockchain.models.account_state import AccountState


@pytest.fixture
def cleanup_for_rollback_and_commit_tests():
    yield
    with transaction.atomic():
        AccountState.objects.all().delete()

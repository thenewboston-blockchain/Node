import pytest
from django.db import transaction
from django.test import override_settings

from node.blockchain.models.account_state import AccountState


@pytest.fixture
def cleanup_for_rollback_and_commit_tests():
    yield
    with transaction.atomic():
        AccountState.objects.all().delete()


@pytest.fixture(autouse=True)
def test_settings(settings):
    with override_settings(
        USE_ON_COMMIT_HOOK=False,
        SECRET_KEY='b27c612c6cbeac10c8788fbc95b29f563cc0ea2eb7d6be08',
        NODE_SIGNING_KEY='a025da120a1c95b27f17bb9442af9c27d3a357733aa150b458f21682a2d539a9',
        CELERY_BROKER_URL='memory://',
        CELERY_TASK_ALWAYS_EAGER=True,
        NODE_SCHEDULE_CAPACITY=20,
    ):
        # For some reason we need to import the app to make celery settings work
        from node.config.celery import app  # noqa: F401
        yield

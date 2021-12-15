import pytest
from django.db import transaction

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import NodeDeclarationSignedChangeRequest
from node.blockchain.models import Block, Lock
from node.blockchain.utils import TableLocker
from node.core.exceptions import BlockchainLockedError


@pytest.mark.django_db
def test_lock_table():
    with TableLocker('db_table'):
        assert Lock.objects.count() == 1
        table_lock = Lock.objects.first()
        assert table_lock.name == 'db_table'
    assert Lock.objects.count() == 0


@pytest.mark.django_db
def test_raise_error_when_table_was_locked_and_expect_locked_is_false(
    node_declaration_signed_change_request_message, regular_node_key_pair
):
    blockchain_facade = BlockchainFacade.get_instance()

    request = NodeDeclarationSignedChangeRequest.create_from_signed_change_request_message(
        message=node_declaration_signed_change_request_message, signing_key=regular_node_key_pair.private
    )

    TableLocker('block').__enter__()
    with pytest.raises(BlockchainLockedError):
        Block.objects.add_block_from_signed_change_request(request, blockchain_facade, expect_locked=False)


@pytest.mark.django_db
def test_add_block_when_expect_locked_is_false(node_declaration_signed_change_request_message, regular_node_key_pair):
    blockchain_facade = BlockchainFacade.get_instance()

    request = NodeDeclarationSignedChangeRequest.create_from_signed_change_request_message(
        message=node_declaration_signed_change_request_message, signing_key=regular_node_key_pair.private
    )

    Block.objects.add_block_from_signed_change_request(request, blockchain_facade)


@pytest.mark.django_db
def test_raise_error_when_expect_locked_is_true_on_unlocked_table(
    node_declaration_signed_change_request_message, regular_node_key_pair
):
    blockchain_facade = BlockchainFacade.get_instance()

    request = NodeDeclarationSignedChangeRequest.create_from_signed_change_request_message(
        message=node_declaration_signed_change_request_message, signing_key=regular_node_key_pair.private
    )

    with pytest.raises(BlockchainLockedError):
        Block.objects.add_block_from_signed_change_request(request, blockchain_facade, expect_locked=True)


# TODO(dmu) CRITICAL: Ensure that `with transaction.atomic()` results into transaction or
#                     save point on MongoDB side
#                     https://thenewboston.atlassian.net/browse/BC-174
@pytest.mark.skip('Need to fix or implement transaction.atomic()')
@pytest.mark.django_db
def test_block_should_not_be_created_if_lock_object_was_deleted():
    table_locker = TableLocker('block')
    table_locker.__enter__()

    Lock.objects.all().delete()

    with pytest.raises(BlockchainLockedError):
        with transaction.atomic():
            block = Block(_id=0, signer='0' * 64, signature='0' * 128)
            Block.objects.add_block(block, validate=False, expect_locked=False)
            assert Block.objects.count() == 1

            table_locker.__exit__(None, None, None)

    assert Block.objects.count() == 0

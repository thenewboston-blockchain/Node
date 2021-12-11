import pytest

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import BlockMessage
from node.blockchain.models import AccountState, Block, Schedule
from node.core.utils.cryptography import is_signature_valid
from node.core.utils.types import Signature, Type


@pytest.mark.django_db
def test_create_from_block_message(
    genesis_block_message, primary_validator_key_pair, primary_validator_node, treasury_account_key_pair,
    treasury_amount
):
    assert not AccountState.objects.all().exists()

    blockchain_facade = BlockchainFacade.get_instance()

    block = Block.objects.add_block_from_block_message(
        message=genesis_block_message,
        blockchain_facade=blockchain_facade,
        signing_key=primary_validator_key_pair.private,
        validate=False,
    )
    assert block.signer == primary_validator_key_pair.public
    assert isinstance(block.message, str)
    assert isinstance(block.signature, str)
    assert is_signature_valid(block.signer, block.message.encode('utf-8'), Signature(block.signature))
    message = BlockMessage.parse_raw(block.message)
    assert message.number == 0
    assert message.identifier is None
    assert message.type == Type.GENESIS
    assert message == genesis_block_message

    # Test rereading the block from the database
    block = Block.objects.get(_id=0)
    assert block.signer == primary_validator_key_pair.public
    assert isinstance(block.message, str)
    assert isinstance(block.signature, str)
    assert is_signature_valid(block.signer, block.message.encode('utf-8'), Signature(block.signature))
    message = BlockMessage.parse_raw(block.message)
    assert message.number == 0
    assert message.identifier is None
    assert message.type == Type.GENESIS
    assert message == genesis_block_message

    # Test account state write-through cache
    assert AccountState.objects.count() == 2
    account_state = AccountState.objects.get(_id=primary_validator_key_pair.public)
    assert account_state.account_lock == primary_validator_key_pair.public
    assert account_state.balance == 0
    assert account_state.node == primary_validator_node.dict()

    account_state = AccountState.objects.get(_id=treasury_account_key_pair.public)
    assert account_state.account_lock == treasury_account_key_pair.public
    assert account_state.balance == treasury_amount

    # Test schedule write-through cache
    schedule = Schedule.objects.order_by('_id').all()
    assert tuple((item._id, item.node_identifier) for item in schedule) == ((0, primary_validator_key_pair.public),)

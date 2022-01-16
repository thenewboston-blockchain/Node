import pytest

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import (
    Block, GenesisBlockMessage, GenesisSignedChangeRequestMessage, SignedChangeRequest
)
from node.blockchain.models import AccountState
from node.blockchain.models import Block as ORMBlock
from node.blockchain.models import Schedule
from node.blockchain.types import AccountLock, Signature, Type
from node.core.utils.cryptography import is_signature_valid


@pytest.mark.django_db
def test_create_from_block_message(
    genesis_block_message, primary_validator_key_pair, primary_validator_node, treasury_account_key_pair,
    treasury_amount
):
    assert not AccountState.objects.all().exists()

    blockchain_facade = BlockchainFacade.get_instance()

    block = ORMBlock.objects.add_block_from_block_message(
        message=genesis_block_message,
        blockchain_facade=blockchain_facade,
        signing_key=primary_validator_key_pair.private,
        validate=False,
    )
    assert block.signer == primary_validator_key_pair.public
    assert isinstance(block.signature, str)
    assert is_signature_valid(
        block.signer, block.message.make_binary_representation_for_cryptography(), Signature(block.signature)
    )
    message = block.message
    assert message.number == 0
    assert message.identifier is None
    assert message.type == Type.GENESIS
    assert message == genesis_block_message

    # Test rereading the block from the database
    orm_block = ORMBlock.objects.get(_id=0)
    block = Block.parse_raw(orm_block.body)
    assert block.signer == primary_validator_key_pair.public
    assert isinstance(block.signature, str)
    assert is_signature_valid(
        block.signer, block.message.make_binary_representation_for_cryptography(), Signature(block.signature)
    )
    message = block.message
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


@pytest.mark.django_db
def test_create_from_alpha_account_root_file(
    primary_validator_key_pair, primary_validator_node, treasury_account_key_pair, account_root_file
):
    assert not AccountState.objects.all().exists()

    blockchain_facade = BlockchainFacade.get_instance()

    request_message = GenesisSignedChangeRequestMessage.create_from_alpha_account_root_file(
        account_lock=AccountLock(primary_validator_key_pair.public),
        account_root_file=account_root_file,
    )

    request = SignedChangeRequest.create_from_signed_change_request_message(
        request_message, primary_validator_key_pair.private
    )

    genesis_block_message = GenesisBlockMessage.create_from_signed_change_request(request, primary_validator_node)

    block = ORMBlock.objects.add_block_from_block_message(
        message=genesis_block_message,
        blockchain_facade=blockchain_facade,
        signing_key=primary_validator_key_pair.private,
        validate=False,
    )
    assert block.signer == primary_validator_key_pair.public
    assert isinstance(block.signature, str)
    assert is_signature_valid(
        block.signer, block.message.make_binary_representation_for_cryptography(), Signature(block.signature)
    )
    message = block.message
    assert message.number == 0
    assert message.identifier is None
    assert message.type == Type.GENESIS
    assert message == genesis_block_message

    # Test rereading the block from the database
    orm_block = ORMBlock.objects.get(_id=0)
    block = Block.parse_raw(orm_block.body)
    assert block.signer == primary_validator_key_pair.public
    assert isinstance(block.signature, str)
    assert is_signature_valid(
        block.signer, block.message.make_binary_representation_for_cryptography(), Signature(block.signature)
    )
    message = block.message
    assert message.number == 0
    assert message.identifier is None
    assert message.type == Type.GENESIS
    assert message == genesis_block_message

    # Test account state write-through cache
    assert AccountState.objects.count() == 4
    account_state = AccountState.objects.get(_id=primary_validator_key_pair.public)
    assert account_state.account_lock == primary_validator_key_pair.public
    assert account_state.balance == 0
    assert account_state.node == primary_validator_node.dict()

    account_state = AccountState.objects.get(_id='8bf7df36676adbc294ba1a78ff9565dd65e2da73e4d46d5e11c7c3a6c803dff7')
    account_root_file_entry = account_root_file['8BF7DF36676ADBC294BA1A78FF9565DD65E2DA73E4D46D5E11C7C3A6C803DFF7']
    assert account_state.account_lock == account_root_file_entry['balance_lock'].lower()
    assert account_state.balance == account_root_file_entry['balance']

    account_state = AccountState.objects.get(_id='009073c5985d3a715c3d44a33d5f928e893935fbab206d1d676d7d8b6e27ec85')

    account_root_file_entry = account_root_file['009073c5985d3a715c3d44a33d5f928e893935fbab206d1d676d7d8b6e27ec85']
    assert account_state.account_lock == account_root_file_entry['balance_lock']
    assert account_state.balance == account_root_file_entry['balance']

    # Test schedule write-through cache
    schedule = Schedule.objects.order_by('_id').all()
    assert tuple((item._id, item.node_identifier) for item in schedule) == ((0, primary_validator_key_pair.public),)

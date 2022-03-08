import pytest

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import (
    AccountState, Block, BlockMessageUpdate, CoinTransferSignedChangeRequest, CoinTransferSignedChangeRequestMessage
)
from node.blockchain.inner_models.signed_change_request_message import CoinTransferTransaction
from node.blockchain.models import AccountState as DBAccountState
from node.blockchain.models.block import Block as ORMBlock
from node.blockchain.types import AccountLock, Signature, Type
from node.core.exceptions import ValidationError
from node.core.utils.cryptography import is_signature_valid


@pytest.mark.django_db
def test_add_block_from_block_message(coin_transfer_block_message, primary_validator_key_pair, treasury_amount):
    blockchain_facade = BlockchainFacade.get_instance()

    expected_block_number = blockchain_facade.get_next_block_number()
    expected_identifier = blockchain_facade.get_next_block_identifier()

    block = blockchain_facade.add_block_from_block_message(
        message=coin_transfer_block_message,
        signing_key=primary_validator_key_pair.private,
        validate=False,
    )
    assert block.signer == primary_validator_key_pair.public
    assert isinstance(block.signature, str)
    assert is_signature_valid(
        block.signer, block.message.make_binary_representation_for_cryptography(), Signature(block.signature)
    )
    message = block.message
    assert message.number == expected_block_number
    assert message.identifier == expected_identifier
    assert message.type == Type.COIN_TRANSFER
    assert message == coin_transfer_block_message

    # Test rereading the block from the database
    orm_block = ORMBlock.objects.get(_id=expected_block_number)
    block = Block.parse_raw(orm_block.body)
    assert block.signer == primary_validator_key_pair.public
    assert isinstance(block.signature, str)
    assert is_signature_valid(
        block.signer, block.message.make_binary_representation_for_cryptography(), Signature(block.signature)
    )
    message = block.message
    assert message.number == expected_block_number
    assert message.identifier == expected_identifier
    assert message.type == Type.COIN_TRANSFER
    assert message == coin_transfer_block_message

    # Test account state write-through cache
    assert DBAccountState.objects.count() == 4
    request = coin_transfer_block_message.request
    account_state = DBAccountState.objects.get(_id=request.signer)
    assert account_state.account_lock == request.make_hash()
    assert account_state.balance == treasury_amount - request.message.get_total_amount()
    assert account_state.node is None


@pytest.mark.usefixtures('base_blockchain')
def test_add_block_from_signed_change_request(
    treasure_coin_transfer_signed_change_request, regular_node, self_node, primary_validator_key_pair, treasury_amount
):
    blockchain_facade = BlockchainFacade.get_instance()

    expected_block_number = blockchain_facade.get_next_block_number()
    expected_identifier = blockchain_facade.get_next_block_identifier()

    block = blockchain_facade.add_block_from_signed_change_request(
        treasure_coin_transfer_signed_change_request, signing_key=primary_validator_key_pair.private
    )
    assert block.signer == primary_validator_key_pair.public
    assert isinstance(block.signature, str)
    assert is_signature_valid(
        block.signer, block.message.make_binary_representation_for_cryptography(), Signature(block.signature)
    )
    message = block.message
    assert message.number == expected_block_number
    assert message.identifier == expected_identifier
    assert message.type == Type.COIN_TRANSFER
    assert message.request == treasure_coin_transfer_signed_change_request
    expected_message_update = BlockMessageUpdate(
        accounts={
            treasure_coin_transfer_signed_change_request.signer:
                AccountState(
                    balance=treasury_amount - treasure_coin_transfer_signed_change_request.message.get_total_amount(),
                    account_lock=treasure_coin_transfer_signed_change_request.make_hash(),
                ),
            regular_node.identifier:
                AccountState(
                    balance=100,
                    account_lock=None,
                ),
            self_node.identifier:
                AccountState(
                    balance=4,
                    account_lock=None,
                ),
        }
    )
    assert message.update == expected_message_update

    orm_block = ORMBlock.objects.get(_id=expected_block_number)
    block = Block.parse_raw(orm_block.body)
    assert block.signer == primary_validator_key_pair.public
    assert isinstance(block.signature, str)
    assert is_signature_valid(
        block.signer, block.message.make_binary_representation_for_cryptography(), Signature(block.signature)
    )
    message = block.message
    assert message.number == expected_block_number
    assert message.identifier == expected_identifier
    assert message.type == Type.COIN_TRANSFER
    assert message.request == treasure_coin_transfer_signed_change_request
    assert message.update == expected_message_update


@pytest.mark.usefixtures('base_blockchain')
def test_add_block_from_signed_change_request_account_lock_validation(
    treasury_account_key_pair, regular_node, self_node
):
    blockchain_facade = BlockchainFacade.get_instance()

    account_lock = AccountLock('0' * 64)
    assert blockchain_facade.get_account_lock(treasury_account_key_pair.public) != account_lock
    message = CoinTransferSignedChangeRequestMessage(
        account_lock=account_lock,
        txs=[
            CoinTransferTransaction(recipient='1' * 64, amount=10),
            CoinTransferTransaction(recipient=self_node.identifier, amount=self_node.fee, is_fee=True),
        ],
    )

    request = CoinTransferSignedChangeRequest.create_from_signed_change_request_message(
        message=message,
        signing_key=treasury_account_key_pair.private,
    )

    with pytest.raises(ValidationError, match='Invalid account lock'):
        blockchain_facade.add_block_from_signed_change_request(request)

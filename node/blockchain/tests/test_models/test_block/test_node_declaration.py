import pytest

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import (
    AccountState, Block, BlockMessageUpdate, Node, NodeDeclarationSignedChangeRequest,
    NodeDeclarationSignedChangeRequestMessage
)
from node.blockchain.models import AccountState as DBAccountState
from node.blockchain.models.block import Block as ORMBlock
from node.blockchain.types import AccountLock, AccountNumber, Signature, Type
from node.core.exceptions import ValidationError
from node.core.utils.cryptography import is_signature_valid


@pytest.mark.django_db
def test_add_block_from_block_message(node_declaration_block_message, primary_validator_key_pair):
    blockchain_facade = BlockchainFacade.get_instance()

    expected_block_number = blockchain_facade.get_next_block_number()
    expected_identifier = blockchain_facade.get_next_block_identifier()

    block = blockchain_facade.add_block_from_block_message(
        message=node_declaration_block_message,
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
    assert message.type == Type.NODE_DECLARATION
    assert message == node_declaration_block_message

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
    assert message.type == Type.NODE_DECLARATION
    assert message == node_declaration_block_message

    # Test account state write-through cache
    assert DBAccountState.objects.count() == 3
    account_state = DBAccountState.objects.get(identifier=node_declaration_block_message.request.signer)
    assert account_state.account_lock == node_declaration_block_message.request.make_hash()
    assert account_state.balance == 0

    orm_node = account_state.node
    node = node_declaration_block_message.request.message.node
    assert orm_node.identifier == node.identifier
    assert orm_node.addresses == node.addresses
    assert orm_node.fee == node.fee


@pytest.mark.usefixtures('base_blockchain')
def test_add_block_from_signed_change_request(
    self_node_declaration_signed_change_request, regular_node_key_pair, primary_validator_key_pair
):
    blockchain_facade = BlockchainFacade.get_instance()

    expected_block_number = blockchain_facade.get_next_block_number()
    expected_identifier = blockchain_facade.get_next_block_identifier()

    block = blockchain_facade.add_block_from_signed_change_request(
        self_node_declaration_signed_change_request, signing_key=primary_validator_key_pair.private
    )
    assert block.signer == primary_validator_key_pair.public
    assert isinstance(block.signature, str)
    assert is_signature_valid(
        block.signer, block.message.make_binary_representation_for_cryptography(), Signature(block.signature)
    )
    message = block.message
    assert message.number == expected_block_number
    assert message.identifier == expected_identifier
    assert message.type == Type.NODE_DECLARATION
    assert message.request == self_node_declaration_signed_change_request
    expected_message_update = BlockMessageUpdate(
        accounts={
            self_node_declaration_signed_change_request.signer:
                AccountState(
                    node=self_node_declaration_signed_change_request.message.node,
                    account_lock=self_node_declaration_signed_change_request.make_hash(),
                )
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
    assert message.type == Type.NODE_DECLARATION
    assert message.request == self_node_declaration_signed_change_request
    assert message.update == expected_message_update


@pytest.mark.usefixtures('base_blockchain')
def test_add_block_from_signed_change_request_account_lock_validation(regular_node_key_pair, regular_node):
    blockchain_facade = BlockchainFacade.get_instance()

    account_lock = AccountLock('0' * 64)
    assert blockchain_facade.get_account_lock(regular_node_key_pair.public) != account_lock
    message = NodeDeclarationSignedChangeRequestMessage(
        account_lock=account_lock,
        node=regular_node,
    )

    request = NodeDeclarationSignedChangeRequest.create_from_signed_change_request_message(
        message=message,
        signing_key=regular_node_key_pair.private,
    )

    with pytest.raises(ValidationError, match='Invalid account lock'):
        blockchain_facade.add_block_from_signed_change_request(request)


@pytest.mark.django_db
def test_add_block_from_signed_change_request_node_identifier_validation(regular_node_key_pair, regular_node):
    account_number = AccountNumber('0' * 64)
    regular_node = Node(
        identifier=account_number,
        addresses=['http://not-existing-node-address-674898923.com:8555/'],
        fee=4,
    )

    message = NodeDeclarationSignedChangeRequestMessage(
        account_lock=regular_node_key_pair.public,
        node=regular_node,
    )

    request = NodeDeclarationSignedChangeRequest.create_from_signed_change_request_message(
        message=message,
        signing_key=regular_node_key_pair.private,
    )

    blockchain_facade = BlockchainFacade.get_instance()
    with pytest.raises(ValidationError, match='Signer does not match with node identifier'):
        blockchain_facade.add_block_from_signed_change_request(request)

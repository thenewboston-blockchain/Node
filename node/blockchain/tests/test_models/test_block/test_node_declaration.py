import pytest

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import (
    AccountState, BlockMessage, BlockMessageUpdate, NodeDeclarationSignedChangeRequest
)
from node.blockchain.models import AccountState as DBAccountState
from node.blockchain.models.block import Block
from node.core.utils.cryptography import get_node_identifier, is_signature_valid
from node.core.utils.types import Signature, Type


@pytest.mark.django_db
def test_add_block_from_block_message(node_declaration_block_message, primary_validator_key_pair):
    blockchain_facade = BlockchainFacade.get_instance()

    expected_block_number = blockchain_facade.get_next_block_number()
    expected_identifier = blockchain_facade.get_next_block_identifier()

    block = Block.objects.add_block_from_block_message(
        message=node_declaration_block_message,
        blockchain_facade=blockchain_facade,
        signing_key=primary_validator_key_pair.private,
        validate=False,
    )
    assert block.signer == primary_validator_key_pair.public
    assert isinstance(block.message, str)
    assert isinstance(block.signature, str)
    assert is_signature_valid(block.signer, block.message.encode('utf-8'), Signature(block.signature))
    message = BlockMessage.parse_raw(block.message)
    assert message.number == expected_block_number
    assert message.identifier == expected_identifier
    assert message.type == Type.NODE_DECLARATION
    assert message == node_declaration_block_message

    # Test rereading the block from the database
    block = Block.objects.get(_id=expected_block_number)
    assert block.signer == primary_validator_key_pair.public
    assert isinstance(block.message, str)
    assert isinstance(block.signature, str)
    assert is_signature_valid(block.signer, block.message.encode('utf-8'), Signature(block.signature))
    message = BlockMessage.parse_raw(block.message)
    assert message.number == expected_block_number
    assert message.identifier == expected_identifier
    assert message.type == Type.NODE_DECLARATION
    assert message == node_declaration_block_message

    # Test write-through cache
    assert DBAccountState.objects.count() == 1
    account_state = DBAccountState.objects.get(_id=node_declaration_block_message.request.signer)
    assert account_state.account_lock == node_declaration_block_message.request.message.make_hash()
    assert account_state.balance == 0
    assert account_state.node == node_declaration_block_message.request.message.node


@pytest.mark.django_db
def test_add_block_from_signed_change_request(node_declaration_signed_change_request_message, regular_node_key_pair):
    blockchain_facade = BlockchainFacade.get_instance()

    expected_block_number = blockchain_facade.get_next_block_number()
    expected_identifier = blockchain_facade.get_next_block_identifier()

    request = NodeDeclarationSignedChangeRequest.create_from_signed_change_request_message(
        message=node_declaration_signed_change_request_message,
        signing_key=regular_node_key_pair.private,
    )

    block = Block.objects.add_block_from_signed_change_request(request, blockchain_facade)
    assert block.signer == get_node_identifier()
    assert isinstance(block.message, str)
    assert isinstance(block.signature, str)
    assert is_signature_valid(block.signer, block.message.encode('utf-8'), Signature(block.signature))
    message = BlockMessage.parse_raw(block.message)
    assert message.number == expected_block_number
    assert message.identifier == expected_identifier
    assert message.type == Type.NODE_DECLARATION
    assert message.request == request
    expected_message_update = BlockMessageUpdate(
        accounts={request.signer: AccountState(
            node=request.message.node,
            account_lock=request.message.make_hash(),
        )}
    )
    assert message.update == expected_message_update

    block = Block.objects.get(_id=expected_block_number)
    assert block.signer == get_node_identifier()
    assert isinstance(block.message, str)
    assert isinstance(block.signature, str)
    assert is_signature_valid(block.signer, block.message.encode('utf-8'), Signature(block.signature))
    message = BlockMessage.parse_raw(block.message)
    assert message.number == expected_block_number
    assert message.identifier == expected_identifier
    assert message.type == Type.NODE_DECLARATION
    assert message.request == request
    assert message.update == expected_message_update

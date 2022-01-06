import pytest

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import BlockMessage, NodeDeclarationSignedChangeRequest
from node.blockchain.models import Block
from node.blockchain.utils.lock import create_lock, delete_lock
from node.core.exceptions import BlockchainLockingError


@pytest.mark.usefixtures('base_blockchain')
def test_cannot_add_block_from_signed_change_request_if_blockchain_is_locked(
    node_declaration_signed_change_request_message, regular_node_key_pair
):
    blockchain_facade = BlockchainFacade.get_instance()

    request = NodeDeclarationSignedChangeRequest.create_from_signed_change_request_message(
        message=node_declaration_signed_change_request_message, signing_key=regular_node_key_pair.private
    )

    create_lock('block')
    with pytest.raises(BlockchainLockingError):
        Block.objects.add_block_from_signed_change_request(request, blockchain_facade)

    delete_lock('block')

    Block.objects.add_block_from_signed_change_request(request, blockchain_facade)


@pytest.mark.usefixtures('base_blockchain')
def test_cannot_add_block_from_block_message_if_blockchain_is_locked(
    node_declaration_signed_change_request_message, regular_node_key_pair
):
    blockchain_facade = BlockchainFacade.get_instance()

    request = NodeDeclarationSignedChangeRequest.create_from_signed_change_request_message(
        message=node_declaration_signed_change_request_message, signing_key=regular_node_key_pair.private
    )
    block_message = BlockMessage.create_from_signed_change_request(request, blockchain_facade)

    create_lock('block')
    with pytest.raises(BlockchainLockingError):
        Block.objects.add_block_from_block_message(block_message, blockchain_facade, validate=False)

    delete_lock('block')

    Block.objects.add_block_from_block_message(block_message, blockchain_facade, validate=False)


@pytest.mark.usefixtures('base_blockchain')
def test_cannot_add_block_if_blockchain_is_locked(
    node_declaration_signed_change_request_message, regular_node_key_pair, primary_validator_key_pair
):
    blockchain_facade = BlockchainFacade.get_instance()

    request = NodeDeclarationSignedChangeRequest.create_from_signed_change_request_message(
        message=node_declaration_signed_change_request_message, signing_key=regular_node_key_pair.private
    )
    block_message = BlockMessage.create_from_signed_change_request(request, blockchain_facade)
    signing_key = primary_validator_key_pair.private
    binary_data, signature = block_message.make_binary_data_and_signature(signing_key)

    block = Block(
        _id=block_message.number,
        signer=primary_validator_key_pair.public,
        signature=signature,
        message=binary_data.decode('utf-8'),
    )
    blockchain_facade.update_write_through_cache(block_message)

    create_lock('block')
    with pytest.raises(BlockchainLockingError):
        Block.objects.add_block(block, validate=False)

    delete_lock('block')

    Block.objects.add_block(block, validate=False)

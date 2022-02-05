import pytest

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import Block, BlockMessage, NodeDeclarationSignedChangeRequest
from node.blockchain.models import Block as ORMBlock
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
        ORMBlock.objects.add_block_from_signed_change_request(request, blockchain_facade)

    delete_lock('block')

    ORMBlock.objects.add_block_from_signed_change_request(request, blockchain_facade)


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
        ORMBlock.objects.add_block_from_block_message(block_message, blockchain_facade, validate=False)

    delete_lock('block')

    ORMBlock.objects.add_block_from_block_message(block_message, blockchain_facade, validate=False)


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
    signature = block_message.make_signature(signing_key)

    block = Block(
        signer=primary_validator_key_pair.public,
        signature=signature,
        message=block_message,
    )

    create_lock('block')
    with pytest.raises(BlockchainLockingError):
        blockchain_facade.add_block(block, validate=False)

    delete_lock('block')

    blockchain_facade.add_block(block, validate=False)

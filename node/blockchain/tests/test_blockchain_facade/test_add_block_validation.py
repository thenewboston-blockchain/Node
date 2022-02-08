import pytest
from pydantic.error_wrappers import ValidationError as PydanticValidationError

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import Block, BlockMessage
from node.blockchain.tests.factories.block import make_block
from node.core.exceptions import ValidationError


@pytest.mark.usefixtures('base_blockchain')
def test_add_block_invalid_signature(node_declaration_block_message):
    block = Block(signer='0' * 64, signature='1' * 128, message=node_declaration_block_message)
    block_json = block.json()

    with pytest.raises(PydanticValidationError, match='Invalid signature'):
        BlockchainFacade.get_instance().add_block_from_json(block_json)


@pytest.mark.usefixtures('base_blockchain')
def test_add_block_invalid_block_identifier(node_declaration_block_message, primary_validator_key_pair):
    block_message_dict = node_declaration_block_message.dict()
    block_message_dict['identifier'] = '0' * 64
    block = make_block(BlockMessage.parse_obj(block_message_dict), primary_validator_key_pair.private)
    block_json = block.json()

    with pytest.raises(ValidationError, match='Invalid identifier'):
        BlockchainFacade.get_instance().add_block_from_json(block_json)


@pytest.mark.usefixtures('rich_blockchain')
def test_add_block_invalid_block_number(node_declaration_block_message, primary_validator_key_pair):
    block_message_dict = node_declaration_block_message.dict()
    block_message_dict['number'] -= 1
    assert block_message_dict['number'] >= 0
    assert block_message_dict['number'] != BlockchainFacade.get_instance().get_next_block_number()

    block = make_block(BlockMessage.parse_obj(block_message_dict), primary_validator_key_pair.private)
    block_json = block.json()

    with pytest.raises(ValidationError, match='Invalid block number'):
        BlockchainFacade.get_instance().add_block_from_json(block_json)


@pytest.mark.usefixtures('base_blockchain')
def test_add_block_invalid_signer(node_declaration_block_message, regular_node_key_pair):
    assert BlockchainFacade.get_instance().get_primary_validator().identifier != regular_node_key_pair.public
    block = make_block(node_declaration_block_message, regular_node_key_pair.private)
    block_json = block.json()

    with pytest.raises(ValidationError, match='Invalid block signer'):
        BlockchainFacade.get_instance().add_block_from_json(block_json)

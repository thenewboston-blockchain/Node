import pytest

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import (
    BlockMessage, GenesisBlockMessage, GenesisSignedChangeRequest, NodeDeclarationSignedChangeRequest
)


@pytest.fixture
def genesis_block_message(genesis_signed_change_request_message, primary_validator_key_pair, primary_validator_node):
    request = GenesisSignedChangeRequest.create_from_signed_change_request_message(
        message=genesis_signed_change_request_message,
        signing_key=primary_validator_key_pair.private,
    )
    return GenesisBlockMessage.create_from_signed_change_request(request, primary_validator_node)


@pytest.fixture
def node_declaration_block_message(node_declaration_signed_change_request_message, regular_node_key_pair):
    request = NodeDeclarationSignedChangeRequest.create_from_signed_change_request_message(
        message=node_declaration_signed_change_request_message,
        signing_key=regular_node_key_pair.private,
    )
    return BlockMessage.create_from_signed_change_request(request, BlockchainFacade.get_instance())

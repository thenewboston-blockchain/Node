import pytest

from node.blockchain.inner_models import GenesisBlockMessage, SignedChangeRequest


@pytest.fixture
def genesis_block_message(genesis_signed_change_request_message, primary_validator_key_pair, primary_validator_node):
    request = SignedChangeRequest.create_from_signed_change_request_message(
        message=genesis_signed_change_request_message,
        signing_key=primary_validator_key_pair.private,
    )
    return GenesisBlockMessage.create_from_signed_change_request(
        request=request, primary_validator_node=primary_validator_node
    )

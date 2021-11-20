import pytest

from node.blockchain.inner_models import GenesisBlockMessage, Node, SignedChangeRequest


@pytest.fixture
def genesis_block_message(genesis_signed_change_request_message, primary_validator_key_pair):
    request = SignedChangeRequest.create_from_signed_change_request_message(
        message=genesis_signed_change_request_message,
        signing_key=primary_validator_key_pair.private,
    )
    node = Node(
        identifier=primary_validator_key_pair.public,
        addresses=['http://non-existing-address-4643256.com:8555/'],
        fee=4,
    )
    return GenesisBlockMessage.create_from_signed_change_request(request=request, primary_validator_node=node)

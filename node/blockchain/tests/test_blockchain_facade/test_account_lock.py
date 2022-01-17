import pytest

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import NodeDeclarationSignedChangeRequest
from node.blockchain.models.block import Block


@pytest.mark.django_db
@pytest.mark.usefixtures('base_blockchain')
def test_account_lock_change_when_block_is_added(
    node_declaration_signed_change_request_message, regular_node_key_pair
):
    blockchain_facade = BlockchainFacade.get_instance()

    assert blockchain_facade.get_account_lock(regular_node_key_pair.public) == regular_node_key_pair.public

    request = NodeDeclarationSignedChangeRequest.create_from_signed_change_request_message(
        message=node_declaration_signed_change_request_message,
        signing_key=regular_node_key_pair.private,
    )

    Block.objects.add_block_from_signed_change_request(request, blockchain_facade)

    account_lock = blockchain_facade.get_account_lock(regular_node_key_pair.public)
    assert account_lock != regular_node_key_pair.public
    assert account_lock == request.make_hash()

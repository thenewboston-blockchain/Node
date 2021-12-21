from node.blockchain.inner_models import AccountState, NodeDeclarationBlockMessage, NodeDeclarationSignedChangeRequest


def test_create_from_signed_change_request(
    node_declaration_signed_change_request_message, regular_node_key_pair, regular_node
):
    request = NodeDeclarationSignedChangeRequest.create_from_signed_change_request_message(
        message=node_declaration_signed_change_request_message,
        signing_key=regular_node_key_pair.private,
    )
    update = NodeDeclarationBlockMessage.make_block_message_update(request)
    assert update.accounts.get(request.signer) == AccountState(
        account_lock=request.make_hash(),
        node=node_declaration_signed_change_request_message.node,
    )
    assert update.schedule is None

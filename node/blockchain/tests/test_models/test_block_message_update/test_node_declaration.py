from node.blockchain.inner_models import (
    AccountState, BlockMessageUpdate, SignedChangeRequest, NodeDeclarationBlockMessageUpdate, NodeDeclarationSignedChangeRequest
)


def test_create_from_signed_change_request(
    node_declaration_signed_change_request_message, primary_validator_key_pair, primary_validator_node
):
    request = SignedChangeRequest.create_from_signed_change_request_message(
        message=node_declaration_signed_change_request_message,
        signing_key=primary_validator_key_pair.private,
    )
    assert isinstance(request, NodeDeclarationSignedChangeRequest)
    update = NodeDeclarationBlockMessageUpdate.create_from_signed_change_request(request)
    raise NotImplementedError
    accounts = genesis_signed_change_request_message.accounts
    assert len(accounts) == 1
    treasury_account_number, expect_treasury_alpha_account = accounts.popitem()
    assert update.accounts.get(treasury_account_number) == AccountState(
        balance=expect_treasury_alpha_account.balance,
        account_lock=expect_treasury_alpha_account.balance_lock,
    )

    assert update.accounts.get(primary_validator_key_pair.public) == AccountState(node=primary_validator_node)
    assert update.schedule == {'0': primary_validator_key_pair.public}

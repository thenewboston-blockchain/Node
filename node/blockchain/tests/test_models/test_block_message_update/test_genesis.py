from node.blockchain.inner_models import AccountState, GenesisBlockMessageUpdate, Node, SignedChangeRequest


def test_create_from_signed_change_request(genesis_signed_change_request_message, primary_validator_key_pair):
    request = SignedChangeRequest.create_from_signed_change_request_message(
        message=genesis_signed_change_request_message,
        signing_key=primary_validator_key_pair.private,
    )
    node = Node(
        identifier=primary_validator_key_pair.public,
        addresses=['http://non-existing-address-4643256.com:8555/'],
        fee=4,
    )
    update = GenesisBlockMessageUpdate.create_from_signed_change_request(request=request, primary_validator_node=node)
    accounts = genesis_signed_change_request_message.accounts
    assert len(accounts) == 1
    treasury_account_number, expect_treasury_alpha_account = accounts.popitem()
    assert update.accounts.get(treasury_account_number) == AccountState(
        balance=expect_treasury_alpha_account.balance,
        account_lock=expect_treasury_alpha_account.balance_lock,
    )

    assert update.accounts.get(primary_validator_key_pair.public) == AccountState(node=node)
    assert update.schedule == {'0': primary_validator_key_pair.public}

from node.blockchain.inner_models import (
    AccountState, BlockMessageUpdate, GenesisBlockMessage, GenesisSignedChangeRequest
)


def test_create_from_signed_change_request(
    genesis_signed_change_request_message, primary_validator_key_pair, primary_validator_node
):
    request = GenesisSignedChangeRequest.create_from_signed_change_request_message(
        message=genesis_signed_change_request_message,
        signing_key=primary_validator_key_pair.private,
    )
    update = GenesisBlockMessage.make_genesis_block_message_update(request, primary_validator_node)
    accounts = genesis_signed_change_request_message.accounts
    assert len(accounts) == 1
    treasury_account_number, expect_treasury_alpha_account = accounts.popitem()
    assert update == BlockMessageUpdate(
        accounts={
            treasury_account_number:
                AccountState(
                    balance=expect_treasury_alpha_account.balance,
                    account_lock=expect_treasury_alpha_account.balance_lock,
                ),
            primary_validator_key_pair.public:
                AccountState(node=primary_validator_node, account_lock=primary_validator_key_pair.public)
        },
        schedule={'0': primary_validator_key_pair.public}
    )

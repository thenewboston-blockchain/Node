from node.blockchain.inner_models.account_state import AccountState
from node.blockchain.inner_models.node import Node
from node.blockchain.inner_models.signed_change_request import GenesisSignedChangeRequest, SignedChangeRequest
from node.blockchain.inner_models.signed_change_request_message import GenesisSignedChangeRequestMessage
from node.core.utils.types import BlockIdentifier, Type


def make_block_message_update_from_signed_change_request(
    request: GenesisSignedChangeRequest, primary_validator_node: Node
):
    assert request.message.type == Type.GENESIS
    assert isinstance(request.message, GenesisSignedChangeRequestMessage)

    accounts = {}
    for account_number, alpha_account in request.message.accounts.items():
        accounts[account_number] = AccountState(
            balance=alpha_account.balance, account_lock=alpha_account.balance_lock
        )

    primary_validator_node_identifier = primary_validator_node.identifier
    primary_validator_account_state = accounts.get(primary_validator_node_identifier)
    if primary_validator_account_state:
        primary_validator_account_state.node = primary_validator_node
    else:
        accounts[primary_validator_node_identifier] = AccountState(node=primary_validator_node)

    schedule = {'0': primary_validator_node_identifier}

    return cls(
        accounts=accounts,
        schedule=schedule,
    )

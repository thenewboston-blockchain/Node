from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import GenesisSignedChangeRequestMessage


def make_genesis_signed_change_request_message(
    primary_validator_account, treasury_account, treasury_amount=281474976710656
) -> GenesisSignedChangeRequestMessage:
    return GenesisSignedChangeRequestMessage.create_from_treasury_account(
        account_lock=BlockchainFacade.get_instance().get_account_lock(primary_validator_account),
        treasury_account_number=treasury_account,
        treasury_amount=treasury_amount
    )

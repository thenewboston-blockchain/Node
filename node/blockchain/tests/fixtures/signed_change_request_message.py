import pytest

from node.blockchain.inner_models import GenesisSignedChangeRequestMessage
from node.core.utils.types import AccountLock


@pytest.fixture
def genesis_signed_change_request_message(primary_validator_key_pair, treasury_account_key_pair, treasury_amount):
    return GenesisSignedChangeRequestMessage.create_from_treasury_account(
        account_lock=AccountLock(primary_validator_key_pair.public),
        treasury_account_number=treasury_account_key_pair.public,
        treasury_amount=treasury_amount
    )

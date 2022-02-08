import pytest

from node.blockchain.tests.factories.block_message.genesis import make_genesis_block_message
from node.blockchain.tests.factories.signed_change_request_message.genesis import (
    make_genesis_signed_change_request_message
)


@pytest.fixture
def genesis_signed_change_request_message(primary_validator_key_pair, treasury_account_key_pair, treasury_amount, db):
    return make_genesis_signed_change_request_message(
        primary_validator_key_pair.public, treasury_account_key_pair.public, treasury_amount
    )


@pytest.fixture
def genesis_block_message(
    genesis_signed_change_request_message, primary_validator_key_pair, primary_validator_node, db
):
    return make_genesis_block_message(
        genesis_signed_change_request_message, primary_validator_key_pair.private, primary_validator_node
    )

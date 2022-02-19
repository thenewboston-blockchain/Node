import pytest

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import BlockMessage
from node.blockchain.tests.factories.signed_change_request.coin_transfer import (
    make_coin_transfer_signed_change_request
)
from node.blockchain.tests.factories.signed_change_request_message.coin_transfer import (
    make_coin_transfer_signed_change_request_message
)


@pytest.fixture
def coin_transfer_signed_change_request_message(
    treasury_account_key_pair, regular_node_key_pair, primary_validator_key_pair, db
):
    return make_coin_transfer_signed_change_request_message(
        treasury_account_key_pair.public,
        regular_node_key_pair.public,  # TODO(dmu) LOW: Better use `user_account`
        primary_validator_key_pair.public,
    )


@pytest.fixture
def treasure_coin_transfer_signed_change_request(
    treasury_account_key_pair, regular_node_key_pair, primary_validator_key_pair, db
):
    return make_coin_transfer_signed_change_request(
        treasury_account_key_pair,
        regular_node_key_pair,  # TODO(dmu) LOW: Better use `user_account`
        primary_validator_key_pair,
    )


@pytest.fixture
def coin_transfer_block_message(treasure_coin_transfer_signed_change_request, base_blockchain, db):
    return BlockMessage.create_from_signed_change_request(
        treasure_coin_transfer_signed_change_request, BlockchainFacade.get_instance()
    )

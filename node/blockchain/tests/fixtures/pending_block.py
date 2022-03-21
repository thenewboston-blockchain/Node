import pytest

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import BlockConfirmation as PydanticBlockConfirmation
from node.blockchain.inner_models import CoinTransferBlockMessage
from node.blockchain.models import BlockConfirmation, PendingBlock
from node.blockchain.tests.factories.block import make_block
from node.blockchain.tests.factories.signed_change_request.coin_transfer import (
    make_coin_transfer_signed_change_request
)


@pytest.fixture
def next_block(
    rich_blockchain, primary_validator_key_pair, treasury_account_key_pair, user_key_pair, regular_node_key_pair
):
    facade = BlockchainFacade.get_instance()
    assert facade.get_primary_validator().identifier == primary_validator_key_pair.public

    request = make_coin_transfer_signed_change_request(
        treasury_account_key_pair, user_key_pair.public, regular_node_key_pair.public
    )
    block_message = CoinTransferBlockMessage.create_from_signed_change_request(request, facade)
    return make_block(block_message, primary_validator_key_pair.private)


@pytest.fixture
def pending_block(rich_blockchain, next_block):
    return PendingBlock.objects.create(
        number=next_block.get_block_number(),
        hash=next_block.make_hash(),
        body=next_block.json(),
    )


@pytest.fixture
def pending_block_confirmations(
    rich_blockchain, pending_block, confirmation_validator_key_pair, confirmation_validator_key_pair_2
):
    block_number = BlockchainFacade.get_instance().get_next_block_number()
    hash_ = pending_block.get_block().make_hash()
    for private_key in (confirmation_validator_key_pair.private, confirmation_validator_key_pair_2.private):
        BlockConfirmation.objects.create_from_block_confirmation(
            PydanticBlockConfirmation.create(number=block_number, hash_=hash_, signing_key=private_key)
        )

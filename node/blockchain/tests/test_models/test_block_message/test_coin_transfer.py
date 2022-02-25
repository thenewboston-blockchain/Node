import re
from datetime import datetime

import pytest
from pydantic import ValidationError

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import (
    AccountState, BlockMessage, BlockMessageUpdate, CoinTransferBlockMessage, CoinTransferSignedChangeRequest
)
from node.blockchain.types import Type


@pytest.mark.usefixtures('base_blockchain')
def test_create_from_signed_change_request(
    coin_transfer_signed_change_request_message, treasury_account_key_pair, treasury_amount
):
    request = CoinTransferSignedChangeRequest.create_from_signed_change_request_message(
        message=coin_transfer_signed_change_request_message,
        signing_key=treasury_account_key_pair.private,
    )
    blockchain_facade = BlockchainFacade.get_instance()
    expected_block_number = blockchain_facade.get_next_block_number()
    expected_identifier = blockchain_facade.get_next_block_identifier()

    message = BlockMessage.create_from_signed_change_request(request, blockchain_facade)
    assert message.number == expected_block_number
    assert message.identifier == expected_identifier
    assert message.type == Type.COIN_TRANSFER
    assert isinstance(message.timestamp, datetime)
    assert message.timestamp.tzinfo is None

    update = message.update
    assert update.accounts.get(request.signer) == AccountState(
        account_lock=request.make_hash(),
        balance=treasury_amount - coin_transfer_signed_change_request_message.get_total_amount(),
    )
    assert update.schedule is None


def test_serialize_deserialize_works(coin_transfer_block_message):
    serialized = coin_transfer_block_message.json()
    deserialized = BlockMessage.parse_raw(serialized)
    assert deserialized.type == coin_transfer_block_message.type
    assert deserialized.number == coin_transfer_block_message.number
    assert deserialized.identifier == coin_transfer_block_message.identifier
    assert deserialized.timestamp == coin_transfer_block_message.timestamp
    assert deserialized.request.signer == coin_transfer_block_message.request.signer
    assert deserialized.request.signature == coin_transfer_block_message.request.signature
    assert deserialized.request.message == coin_transfer_block_message.request.message
    assert deserialized.request == coin_transfer_block_message.request
    assert deserialized.update == coin_transfer_block_message.update
    assert deserialized == coin_transfer_block_message

    serialized2 = deserialized.json()
    assert serialized == serialized2


def test_block_identifier_is_mandatory(treasure_coin_transfer_signed_change_request, treasury_account_key_pair):
    CoinTransferBlockMessage(
        number=1,
        identifier='0' * 64,
        timestamp=datetime.utcnow(),
        request=treasure_coin_transfer_signed_change_request,
        update=BlockMessageUpdate(accounts={'0' * 64: AccountState(balance=10)}),
    )

    with pytest.raises(ValidationError) as exc_info:
        CoinTransferBlockMessage(
            number=1,
            identifier=None,
            timestamp=datetime.utcnow(),
            request=treasure_coin_transfer_signed_change_request,
            update=BlockMessageUpdate(accounts={'0' * 64: AccountState(balance=10)}),
        )

    assert re.search(r'identifier.*none is not an allowed value', str(exc_info.value), flags=re.DOTALL)

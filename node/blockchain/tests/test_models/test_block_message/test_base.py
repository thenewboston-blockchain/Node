import re
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError as PydanticValidationError

from node.blockchain.inner_models import AccountState, BlockMessage, BlockMessageUpdate, CoinTransferBlockMessage
from node.core.exceptions import ValidationError


def test_block_message_timestamp_should_not_be_none(
    treasure_coin_transfer_signed_change_request, treasury_account_key_pair
):
    with pytest.raises(PydanticValidationError) as exc_info:
        CoinTransferBlockMessage(
            number=1,
            identifier='0' * 64,
            timestamp=None,
            request=treasure_coin_transfer_signed_change_request,
            update=BlockMessageUpdate(accounts={'0' * 64: AccountState(balance=10)}),
        )

    assert re.search(r'timestamp.*none is not an allowed value', str(exc_info.value), flags=re.DOTALL)


def test_serialize_deserialize_block_message_timestamp(
    treasure_coin_transfer_signed_change_request, treasury_account_key_pair
):
    block_message = CoinTransferBlockMessage(
        number=1,
        identifier='0' * 64,
        timestamp=datetime.utcnow(),
        request=treasure_coin_transfer_signed_change_request,
        update=BlockMessageUpdate(accounts={'0' * 64: AccountState(balance=10)}),
    )

    timestamp = block_message.dict()['timestamp']
    assert isinstance(timestamp, datetime)
    assert timestamp.tzinfo is None

    serialized = block_message.json()
    deserialized = BlockMessage.parse_raw(serialized)
    timestamp = deserialized.timestamp
    assert isinstance(timestamp, datetime)
    assert timestamp.tzinfo is None


def test_aware_datetime_should_raise_error(treasure_coin_transfer_signed_change_request, treasury_account_key_pair):
    with pytest.raises(ValidationError, match='Timestamp without timezone is expected'):
        CoinTransferBlockMessage(
            number=1,
            identifier='0' * 64,
            timestamp=datetime.now(timezone.utc),
            request=treasure_coin_transfer_signed_change_request,
            update=BlockMessageUpdate(accounts={'0' * 64: AccountState(balance=10)}),
        )

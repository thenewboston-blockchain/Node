import json
from datetime import datetime

import pytest
from pydantic.error_wrappers import ValidationError as PydanticValidationError

from node.blockchain.inner_models import (
    AccountState, BlockMessage, BlockMessageUpdate, GenesisBlockMessage, GenesisSignedChangeRequest
)
from node.blockchain.types import Type


def test_create_from_signed_change_request(
    genesis_signed_change_request_message, primary_validator_key_pair, primary_validator_node
):
    request = GenesisSignedChangeRequest.create_from_signed_change_request_message(
        message=genesis_signed_change_request_message,
        signing_key=primary_validator_key_pair.private,
    )
    message = GenesisBlockMessage.create_from_signed_change_request(request, primary_validator_node)
    assert message.number == 0
    assert message.identifier is None
    assert message.type == Type.GENESIS
    assert isinstance(message.timestamp, datetime)
    assert message.timestamp.tzinfo is None

    accounts = genesis_signed_change_request_message.accounts
    assert len(accounts) == 1
    treasury_account_number, expect_treasury_alpha_account = accounts.popitem()
    assert message.update.accounts.get(treasury_account_number) == AccountState(
        balance=expect_treasury_alpha_account.balance,
        account_lock=expect_treasury_alpha_account.balance_lock,
    )

    assert message.update.accounts.get(
        primary_validator_key_pair.public
    ) == AccountState(node=primary_validator_node, account_lock=primary_validator_key_pair.public)
    assert message.update.schedule == {'0': primary_validator_key_pair.public}


def test_serialize_deserialize_works(genesis_block_message):
    serialized = genesis_block_message.json()
    deserialized = BlockMessage.parse_raw(serialized)
    assert deserialized.type == genesis_block_message.type
    assert deserialized.number == genesis_block_message.number
    assert deserialized.identifier == genesis_block_message.identifier
    assert deserialized.timestamp == genesis_block_message.timestamp
    assert deserialized.request.signer == genesis_block_message.request.signer
    assert deserialized.request.signature == genesis_block_message.request.signature
    assert deserialized.request.message == genesis_block_message.request.message
    assert deserialized.request == genesis_block_message.request
    assert deserialized.update == genesis_block_message.update
    assert deserialized == genesis_block_message

    serialized2 = deserialized.json()
    assert serialized == serialized2


@pytest.mark.parametrize('kwargs', (
    {
        'number': 1
    },
    {
        'identifier': '0' * 64
    },
    {
        'type': Type.NODE_DECLARATION.value
    },
))
def test_cannot_create_invalid_genesis_block_message(
    primary_validator_key_pair, genesis_signed_change_request_message, kwargs
):
    request = GenesisSignedChangeRequest.create_from_signed_change_request_message(
        message=genesis_signed_change_request_message,
        signing_key=primary_validator_key_pair.private,
    )

    with pytest.raises(PydanticValidationError):
        GenesisBlockMessage(
            timestamp=datetime.utcnow(),
            update=BlockMessageUpdate(),
            request=request,
            **(dict(kwargs, type=Type(kwargs['type'])) if 'type' in kwargs else kwargs),
        )

    message = GenesisBlockMessage(
        timestamp=datetime.utcnow(),
        update=BlockMessageUpdate(accounts={'0' * 64: AccountState()}),
        request=request,
    )
    message_dict = json.loads(message.json())
    message_dict.update(kwargs)

    with pytest.raises(PydanticValidationError):
        GenesisBlockMessage.parse_raw(json.dumps(message_dict))

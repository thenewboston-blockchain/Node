from datetime import datetime

from node.blockchain.inner_models import AccountState, BlockMessage, GenesisBlockMessage, Node, SignedChangeRequest
from node.core.utils.types import Type


def test_create_from_signed_change_request(genesis_signed_change_request_message, primary_validator_key_pair):
    request = SignedChangeRequest.create_from_signed_change_request_message(
        message=genesis_signed_change_request_message,
        signing_key=primary_validator_key_pair.private,
    )
    node = Node(
        identifier=primary_validator_key_pair.public,
        addresses=['http://non-existing-address-4643256.com:8555/'],
        fee=4,
    )
    message = GenesisBlockMessage.create_from_signed_change_request(request=request, primary_validator_node=node)
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

    assert message.update.accounts.get(primary_validator_key_pair.public) == AccountState(node=node)
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

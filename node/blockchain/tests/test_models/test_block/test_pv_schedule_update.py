import pytest

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import (
    Block, BlockMessageUpdate, PVScheduleUpdateSignedChangeRequest, PVScheduleUpdateSignedChangeRequestMessage
)
from node.blockchain.models import Schedule
from node.blockchain.models.block import Block as ORMBlock
from node.blockchain.tests.base import as_role
from node.blockchain.types import AccountLock, NodeRole, Signature, Type
from node.core.exceptions import ValidationError
from node.core.utils.cryptography import is_signature_valid


@pytest.mark.django_db
def test_add_block_from_block_message(pv_schedule_update_block_message, primary_validator_key_pair):
    blockchain_facade = BlockchainFacade.get_instance()

    expected_block_number = blockchain_facade.get_next_block_number()
    expected_identifier = blockchain_facade.get_next_block_identifier()

    block = blockchain_facade.add_block_from_block_message(
        message=pv_schedule_update_block_message,
        signing_key=primary_validator_key_pair.private,
        validate=False,
    )
    assert block.signer == primary_validator_key_pair.public
    assert isinstance(block.signature, str)
    assert is_signature_valid(
        block.signer, block.message.make_binary_representation_for_cryptography(), Signature(block.signature)
    )
    message = block.message
    assert message.number == expected_block_number
    assert message.identifier == expected_identifier
    assert message.type == Type.PV_SCHEDULE_UPDATE
    assert message == pv_schedule_update_block_message

    # Test rereading the block from the database
    orm_block = ORMBlock.objects.get(_id=expected_block_number)
    block = Block.parse_raw(orm_block.body)
    assert block.signer == primary_validator_key_pair.public
    assert isinstance(block.signature, str)
    assert is_signature_valid(
        block.signer, block.message.make_binary_representation_for_cryptography(), Signature(block.signature)
    )
    message = block.message
    assert message.number == expected_block_number
    assert message.identifier == expected_identifier
    assert message.type == Type.PV_SCHEDULE_UPDATE
    assert message == pv_schedule_update_block_message

    # Test account state write-through cache
    assert Schedule.objects.count() == 1
    schedule = pv_schedule_update_block_message.request.message.schedule

    for id_, node_identifier in schedule.items():
        assert Schedule.objects.get(_id=id_).node_identifier == node_identifier


@pytest.mark.usefixtures('base_blockchain')
def test_add_block_from_signed_change_request(pv_schedule_update_signed_change_request, primary_validator_key_pair):
    blockchain_facade = BlockchainFacade.get_instance()

    expected_block_number = blockchain_facade.get_next_block_number()
    expected_identifier = blockchain_facade.get_next_block_identifier()

    block = blockchain_facade.add_block_from_signed_change_request(
        pv_schedule_update_signed_change_request, signing_key=primary_validator_key_pair.private
    )
    assert block.signer == primary_validator_key_pair.public
    assert isinstance(block.signature, str)
    assert is_signature_valid(
        block.signer, block.message.make_binary_representation_for_cryptography(), Signature(block.signature)
    )
    message = block.message
    assert message.number == expected_block_number
    assert message.identifier == expected_identifier
    assert message.type == Type.PV_SCHEDULE_UPDATE
    assert message.request == pv_schedule_update_signed_change_request
    expected_message_update = BlockMessageUpdate(schedule={'1': primary_validator_key_pair.public})
    assert message.update == expected_message_update

    orm_block = ORMBlock.objects.get(_id=expected_block_number)
    block = Block.parse_raw(orm_block.body)
    assert block.signer == primary_validator_key_pair.public
    assert isinstance(block.signature, str)
    assert is_signature_valid(
        block.signer, block.message.make_binary_representation_for_cryptography(), Signature(block.signature)
    )
    message = block.message
    assert message.number == expected_block_number
    assert message.identifier == expected_identifier
    assert message.type == Type.PV_SCHEDULE_UPDATE
    assert message.request == pv_schedule_update_signed_change_request
    assert message.update == expected_message_update


@pytest.mark.usefixtures('base_blockchain')
def test_add_block_from_signed_change_request_account_lock_validation(primary_validator_key_pair):
    blockchain_facade = BlockchainFacade.get_instance()

    account_lock = AccountLock('0' * 64)
    assert blockchain_facade.get_account_lock(primary_validator_key_pair.public) != account_lock
    message = PVScheduleUpdateSignedChangeRequestMessage(
        account_lock=account_lock,
        schedule={'1': primary_validator_key_pair.public},
    )

    request = PVScheduleUpdateSignedChangeRequest.create_from_signed_change_request_message(
        message=message,
        signing_key=primary_validator_key_pair.private,
    )

    with pytest.raises(ValidationError, match='Invalid account lock'):
        blockchain_facade.add_block_from_signed_change_request(request)


@pytest.mark.usefixtures('base_blockchain')
def test_invalid_account_lock(primary_validator_key_pair):
    blockchain_facade = BlockchainFacade.get_instance()

    pv_schedule_update_signed_change_request_message = PVScheduleUpdateSignedChangeRequestMessage(
        account_lock='0' * 64, schedule={'1': primary_validator_key_pair.public}
    )
    request = PVScheduleUpdateSignedChangeRequest.create_from_signed_change_request_message(
        message=pv_schedule_update_signed_change_request_message,
        signing_key=primary_validator_key_pair.private,
    )
    with pytest.raises(ValidationError, match='Invalid account lock'):
        blockchain_facade.add_block_from_signed_change_request(request)


@pytest.mark.usefixtures('base_blockchain')
def test_validate_nodes_are_declared(primary_validator_key_pair):
    blockchain_facade = BlockchainFacade.get_instance()

    pv_schedule_update_signed_change_request_message = PVScheduleUpdateSignedChangeRequestMessage(
        account_lock=blockchain_facade.get_account_lock(primary_validator_key_pair.public),
        schedule={
            '1': primary_validator_key_pair.public,
            '100': '1' * 64,
        }
    )
    request = PVScheduleUpdateSignedChangeRequest.create_from_signed_change_request_message(
        message=pv_schedule_update_signed_change_request_message,
        signing_key=primary_validator_key_pair.private,
    )
    with pytest.raises(ValidationError, match='All nodes in the schedule must be declared'):
        blockchain_facade.add_block_from_signed_change_request(request)


@as_role(NodeRole.PRIMARY_VALIDATOR)
@pytest.mark.parametrize(
    'schedule_keys,exception_match', (
        (['0'], None),
        (['0', '100', '200'], None),
        (['1'], None),
        (['3'], None),
        (['3', '200', '100'], None),
        (['1', '3', '5'], 'Outdated block numbers detected in schedule'),
        (['1', '2'], 'Outdated block numbers detected in schedule'),
        (['100'], 'Schedule with lowest key must cover next block number'),
        (['100', '200', '300'], 'Schedule with lowest key must cover next block number'),
    )
)
@pytest.mark.usefixtures('rich_blockchain')
def test_validate_block_numbers(schedule_keys, exception_match, primary_validator_node, self_node_key_pair):
    blockchain_facade = BlockchainFacade.get_instance()
    assert blockchain_facade.get_next_block_number() == 7

    schedule = {k: primary_validator_node.identifier for k in schedule_keys}

    pv_schedule_update_signed_change_request_message = PVScheduleUpdateSignedChangeRequestMessage(
        account_lock=blockchain_facade.get_account_lock(self_node_key_pair.public), schedule=schedule
    )
    request = PVScheduleUpdateSignedChangeRequest.create_from_signed_change_request_message(
        message=pv_schedule_update_signed_change_request_message,
        signing_key=self_node_key_pair.private,
    )
    if exception_match:
        with pytest.raises(ValidationError, match=exception_match):
            blockchain_facade.add_block_from_signed_change_request(request)
    else:
        blockchain_facade.add_block_from_signed_change_request(request)

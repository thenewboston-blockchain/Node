import pytest

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import PVScheduleUpdateSignedChangeRequestMessage, SignedChangeRequest
from node.blockchain.inner_models.signed_change_request import PVScheduleUpdateSignedChangeRequest
from node.core.exceptions import ValidationError


def test_create_from_pv_schedule_update_signed_change_request_message(
    pv_schedule_update_signed_change_request_message, regular_node_key_pair
):
    signed_change_request = SignedChangeRequest.create_from_signed_change_request_message(
        message=pv_schedule_update_signed_change_request_message,
        signing_key=regular_node_key_pair.private,
    )
    assert isinstance(signed_change_request, PVScheduleUpdateSignedChangeRequest)
    assert signed_change_request.message == pv_schedule_update_signed_change_request_message
    assert signed_change_request.signer == regular_node_key_pair.public
    assert signed_change_request.signature == (
        'be5830a0520b3537bac59f6a750eff876db4122a4608942f87f2324495e9a238'
        '95b1a7de8fc6d80626a32e704370b81d7a1a2d17c50254fb506924a87d3f4e0b'
    )


def test_serialize_and_deserialize_pv_schedule_update(pv_schedule_update_signed_change_request):
    assert isinstance(pv_schedule_update_signed_change_request, PVScheduleUpdateSignedChangeRequest)
    serialized = pv_schedule_update_signed_change_request.json()
    deserialized = SignedChangeRequest.parse_raw(serialized)
    assert isinstance(deserialized, PVScheduleUpdateSignedChangeRequest)
    assert deserialized.signer == pv_schedule_update_signed_change_request.signer
    assert deserialized.signature == pv_schedule_update_signed_change_request.signature
    assert deserialized.message == pv_schedule_update_signed_change_request.message
    assert deserialized == pv_schedule_update_signed_change_request

    serialized2 = deserialized.json()
    assert serialized == serialized2


# TODO CRITICAL: Implement make_block_message_update for PV Schedule Update
#               https://thenewboston.atlassian.net/browse/BC-232
@pytest.mark.django_db
@pytest.mark.usefixtures('base_blockchain')
@pytest.mark.skip('PVScheduleUpdateBlockMessage.make_block_message_update must be implemented first')
def test_invalid_account_lock(primary_validator_key_pair):
    blockchain_facade = BlockchainFacade.get_instance()

    pv_schedule_update_signed_change_request_message = PVScheduleUpdateSignedChangeRequestMessage(
        account_lock='0' * 64, schedule={}
    )
    request = PVScheduleUpdateSignedChangeRequest.create_from_signed_change_request_message(
        message=pv_schedule_update_signed_change_request_message,
        signing_key=primary_validator_key_pair.private,
    )
    with pytest.raises(ValidationError, match='Invalid account lock'):
        blockchain_facade.add_block_from_signed_change_request(request)

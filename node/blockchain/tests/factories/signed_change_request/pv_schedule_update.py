from node.blockchain.inner_models import PVScheduleUpdateSignedChangeRequest
from node.blockchain.types import AccountNumber, KeyPair
from node.core.utils.types import non_negative_intstr

from ..signed_change_request_message.pv_schedule_update import make_pv_schedule_update_signed_change_request_message


def make_pv_schedule_update_signed_change_request(
    schedule: dict[non_negative_intstr, AccountNumber], primary_validator_key_pair: KeyPair
) -> PVScheduleUpdateSignedChangeRequest:
    signed_change_request = PVScheduleUpdateSignedChangeRequest.create_from_signed_change_request_message(
        message=make_pv_schedule_update_signed_change_request_message(schedule, primary_validator_key_pair.public),
        signing_key=primary_validator_key_pair.private,  # only PV can sign such requests
    )
    assert signed_change_request.message
    assert signed_change_request.signer
    assert signed_change_request.signature

    return signed_change_request

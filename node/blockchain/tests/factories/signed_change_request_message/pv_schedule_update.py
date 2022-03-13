from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models.signed_change_request_message import PVScheduleUpdateSignedChangeRequestMessage
from node.blockchain.types import AccountNumber
from node.core.utils.types import non_negative_intstr


def make_pv_schedule_update_signed_change_request_message(
    schedule: dict[non_negative_intstr, AccountNumber], signer
) -> PVScheduleUpdateSignedChangeRequestMessage:
    return PVScheduleUpdateSignedChangeRequestMessage(
        schedule=schedule, account_lock=BlockchainFacade.get_instance().get_account_lock(signer)
    )

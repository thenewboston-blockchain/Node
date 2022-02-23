from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import Node
from node.blockchain.inner_models.signed_change_request_message import PVScheduleUpdateSignedChangeRequestMessage


def make_pv_schedule_update_signed_change_request_message(node: Node) -> PVScheduleUpdateSignedChangeRequestMessage:
    return PVScheduleUpdateSignedChangeRequestMessage(
        schedule={
            '1': node.identifier,
        },
        account_lock=BlockchainFacade.get_instance().get_account_lock(node.identifier),
    )

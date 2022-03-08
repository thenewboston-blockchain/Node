from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import CoinTransferSignedChangeRequestMessage
from node.blockchain.inner_models.signed_change_request_message.coin_transfer import CoinTransferTransaction


def make_coin_transfer_signed_change_request_message(
    sender_account, recipient_account, node_account
) -> CoinTransferSignedChangeRequestMessage:
    return CoinTransferSignedChangeRequestMessage(
        account_lock=BlockchainFacade.get_instance().get_account_lock(sender_account),
        txs=[
            CoinTransferTransaction(recipient=recipient_account, amount=100, is_fee=False, memo='payment'),
            CoinTransferTransaction(recipient=node_account, amount=4, is_fee=True, memo='fee'),
        ]
    )

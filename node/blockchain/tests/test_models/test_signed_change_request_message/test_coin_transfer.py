import pytest
from pydantic import ValidationError

from node.blockchain.inner_models.signed_change_request_message.coin_transfer import CoinTransferTransaction
from node.blockchain.types import Type


@pytest.mark.parametrize('amount', (-3, -3.1, 0, 3.1, '-3', '3'))
def test_coin_transfer_transaction_amount_should_be_positive_integer(amount):
    with pytest.raises(ValidationError):
        CoinTransferTransaction(recipient='0' * 64, amount=amount, is_fee=True, memo='message')


@pytest.mark.parametrize('memo', (True, 1, -3, 0))
def test_coin_transfer_transaction_memo_should_be_strict_string(memo):
    with pytest.raises(ValidationError):
        CoinTransferTransaction(recipient='0' * 64, amount=3, is_fee=True, memo=memo)


@pytest.mark.parametrize('is_fee', ('True', 'False', 1, 0))
def test_coin_transfer_transaction_is_fee_should_be_strict_boolean(is_fee):
    with pytest.raises(ValidationError):
        CoinTransferTransaction(recipient='0' * 64, amount=3, is_fee=is_fee, memo='message')


def test_create_coin_transfer_signed_change_request_message(coin_transfer_signed_change_request_message):
    assert coin_transfer_signed_change_request_message.type == Type.COIN_TRANSFER

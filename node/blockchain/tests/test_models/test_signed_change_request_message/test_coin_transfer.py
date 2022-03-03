import json
import re

import pytest
from pydantic import ValidationError as PydanticValidationError

from node.blockchain.inner_models.signed_change_request_message.coin_transfer import (
    CoinTransferSignedChangeRequestMessage, CoinTransferTransaction
)
from node.blockchain.tests.test_models.base import CREATE, VALID, coin_transfer_message_type_validation_parametrizer
from node.blockchain.types import Type
from node.core.exceptions import ValidationError


@pytest.mark.parametrize('amount', (-3, -3.1, 0, 3.1, '-3', '3'))
def test_coin_transfer_transaction_amount_should_be_positive_integer(amount):
    with pytest.raises(PydanticValidationError):
        CoinTransferTransaction(recipient='0' * 64, amount=amount, is_fee=True, memo='message')


@pytest.mark.parametrize('memo', (True, 1, -3, 0))
def test_coin_transfer_transaction_memo_should_be_strict_string(memo):
    with pytest.raises(PydanticValidationError):
        CoinTransferTransaction(recipient='0' * 64, amount=3, is_fee=True, memo=memo)


@pytest.mark.parametrize('is_fee', ('True', 'False', 1, 0))
def test_coin_transfer_transaction_is_fee_should_be_strict_boolean(is_fee):
    with pytest.raises(PydanticValidationError):
        CoinTransferTransaction(recipient='0' * 64, amount=3, is_fee=is_fee, memo='message')


def test_coin_transfer_should_contain_at_least_one_transaction():
    with pytest.raises(ValidationError, match='Request should contain at least one transaction'):
        CoinTransferSignedChangeRequestMessage(account_lock='0' * 64, txs=[])


def test_create_coin_transfer_signed_change_request_message(coin_transfer_signed_change_request_message):
    assert coin_transfer_signed_change_request_message.type == Type.COIN_TRANSFER


@coin_transfer_message_type_validation_parametrizer
def test_type_validation_on_instantiation(
    id_, account_lock, transaction, recipient, is_fee, amount, memo, search_re, expected_response_body
):
    with pytest.raises(PydanticValidationError) as exc_info:
        if transaction is VALID:
            transaction = CoinTransferTransaction(recipient='0' * 64, amount=10, is_fee=True, memo='message')
        elif transaction is CREATE:
            transaction = CoinTransferTransaction(
                recipient='0' * 64 if recipient is VALID else recipient,
                amount=10 if amount is VALID else amount,
                is_fee=True if is_fee is VALID else is_fee,
                memo='message' if memo is VALID else memo,
            )

        CoinTransferSignedChangeRequestMessage(
            account_lock='0' * 64 if account_lock is VALID else account_lock, txs=[
                transaction,
            ]
        )
    assert re.search(search_re, str(exc_info.value), flags=re.DOTALL)


@coin_transfer_message_type_validation_parametrizer
def test_type_validation_on_parsing(
    id_, account_lock, transaction, recipient, is_fee, amount, memo, search_re, expected_response_body
):
    tx = CoinTransferTransaction(recipient='0' * 64, amount=10, is_fee=True, memo='message')
    serialized = {
        'account_lock':
            '0' * 64 if account_lock is VALID else account_lock,
        'txs': [
            tx.dict() if transaction is VALID else ({
                'recipient': tx.recipient if recipient is VALID else recipient,
                'is_fee': tx.is_fee if is_fee is VALID else is_fee,
                'amount': tx.amount if amount is VALID else amount,
                'memo': tx.memo if memo is VALID else memo,
            } if transaction is CREATE else transaction)
        ]
    }
    serialized_json = json.dumps(serialized)
    with pytest.raises(PydanticValidationError) as exc_info:
        CoinTransferSignedChangeRequestMessage.parse_raw(serialized_json)

    assert re.search(search_re, str(exc_info.value), flags=re.DOTALL)

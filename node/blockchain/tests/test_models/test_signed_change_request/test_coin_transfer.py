import json
import re

import pytest
from pydantic import ValidationError as PydanticValidationError

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import SignedChangeRequest
from node.blockchain.inner_models.signed_change_request import CoinTransferSignedChangeRequest
from node.blockchain.inner_models.signed_change_request_message import (
    CoinTransferSignedChangeRequestMessage, CoinTransferTransaction
)
from node.blockchain.tests.test_models.base import CREATE, VALID, coin_transfer_message_type_validation_parametrizer
from node.core.exceptions import ValidationError


def test_create_from_coin_transfer_signed_change_request_message(
    coin_transfer_signed_change_request_message, treasury_account_key_pair
):
    signed_change_request = SignedChangeRequest.create_from_signed_change_request_message(
        message=coin_transfer_signed_change_request_message,
        signing_key=treasury_account_key_pair.private,
    )
    assert isinstance(signed_change_request, CoinTransferSignedChangeRequest)
    assert signed_change_request.message == coin_transfer_signed_change_request_message
    assert signed_change_request.signer == treasury_account_key_pair.public
    assert signed_change_request.signature == (
        '628b293aeceec992d094c62f60f5031879b4893047f4c4ab158e506c04b916b0'
        '489b5a750d3b1af7cfe9b99c03253424b483450bcafe1b1f608529cad012a502'
    )


def test_serialize_and_deserialize_coin_transfer(
    treasure_coin_transfer_signed_change_request, treasury_account_key_pair
):
    assert isinstance(treasure_coin_transfer_signed_change_request, CoinTransferSignedChangeRequest)
    serialized = treasure_coin_transfer_signed_change_request.json()
    deserialized = SignedChangeRequest.parse_raw(serialized)
    assert isinstance(deserialized, CoinTransferSignedChangeRequest)
    assert deserialized.signer == treasure_coin_transfer_signed_change_request.signer
    assert deserialized.signature == treasure_coin_transfer_signed_change_request.signature
    assert deserialized.message == treasure_coin_transfer_signed_change_request.message
    assert deserialized == treasure_coin_transfer_signed_change_request

    serialized2 = deserialized.json()
    assert serialized == serialized2


@pytest.mark.usefixtures('base_blockchain', 'as_primary_validator')
def test_coin_transfer(
    treasure_coin_transfer_signed_change_request, treasury_account_key_pair, regular_node, self_node, treasury_amount
):
    blockchain_facade = BlockchainFacade.get_instance()
    blockchain_facade.add_block_from_signed_change_request(treasure_coin_transfer_signed_change_request)

    total_amount = treasure_coin_transfer_signed_change_request.message.get_total_amount()
    assert blockchain_facade.get_account_balance(treasury_account_key_pair.public) == treasury_amount - total_amount
    assert blockchain_facade.get_account_balance(regular_node.identifier) == 100
    assert blockchain_facade.get_account_balance(self_node.identifier) == 4


@pytest.mark.usefixtures('base_blockchain')
def test_invalid_account_lock(treasury_account_key_pair, self_node):
    blockchain_facade = BlockchainFacade.get_instance()

    request = CoinTransferSignedChangeRequest.create_from_signed_change_request_message(
        message=CoinTransferSignedChangeRequestMessage(
            account_lock='0' * 64,
            txs=[
                CoinTransferTransaction(recipient='0' * 64, amount=10),
                CoinTransferTransaction(recipient=self_node.identifier, amount=self_node.fee, is_fee=True),
            ]
        ),
        signing_key=treasury_account_key_pair.private,
    )
    with pytest.raises(ValidationError, match='Invalid account lock'):
        blockchain_facade.add_block_from_signed_change_request(request)


@pytest.mark.usefixtures('base_blockchain', 'as_primary_validator')
def test_validate_amount_when_balance_is_not_enough(
    treasure_coin_transfer_signed_change_request, regular_node_key_pair, self_node
):
    blockchain_facade = BlockchainFacade.get_instance()

    blockchain_facade.add_block_from_signed_change_request(treasure_coin_transfer_signed_change_request)
    assert blockchain_facade.get_account_balance(regular_node_key_pair.public) == 100

    signed_change_request_message = CoinTransferSignedChangeRequestMessage(
        account_lock='0' * 64,
        txs=[
            CoinTransferTransaction(recipient='0' * 64, amount=150),
            CoinTransferTransaction(recipient=self_node.identifier, amount=self_node.fee, is_fee=True)
        ]
    )
    request = CoinTransferSignedChangeRequest.create_from_signed_change_request_message(
        message=signed_change_request_message,
        signing_key=regular_node_key_pair.private,
    )
    matched_message = 'Sender account 1c8e5f54a15b63a9f3d540ce505fd0799575ffeaac62ce625c917e6d915ea8bb ' \
                      'balance is not enough to send 154 coins'
    with pytest.raises(ValidationError, match=matched_message):
        blockchain_facade.add_block_from_signed_change_request(request)


@pytest.mark.usefixtures('base_blockchain', 'as_primary_validator')
def test_validate_circular_transactions(treasury_account_key_pair, regular_node_key_pair):
    blockchain_facade = BlockchainFacade.get_instance()
    signed_change_request_message = CoinTransferSignedChangeRequestMessage(
        account_lock=blockchain_facade.get_account_lock(treasury_account_key_pair.public),
        txs=[
            CoinTransferTransaction(recipient=regular_node_key_pair.public, amount=100),
            CoinTransferTransaction(recipient=treasury_account_key_pair.public, amount=100),
        ]
    )

    request = CoinTransferSignedChangeRequest.create_from_signed_change_request_message(
        message=signed_change_request_message,
        signing_key=treasury_account_key_pair.private,
    )

    with pytest.raises(ValidationError, match='Circular transactions detected'):
        blockchain_facade.add_block_from_signed_change_request(request)


@pytest.mark.usefixtures('base_blockchain', 'as_primary_validator')
def test_validate_node_fee_when_send_coins_through_itself(
    treasury_account_key_pair, self_node, self_node_key_pair, regular_node
):
    blockchain_facade = BlockchainFacade.get_instance()

    signed_change_request_message = CoinTransferSignedChangeRequestMessage(
        account_lock=blockchain_facade.get_account_lock(treasury_account_key_pair.public),
        txs=[
            CoinTransferTransaction(recipient=self_node.identifier, amount=100),
            CoinTransferTransaction(recipient=self_node.identifier, amount=self_node.fee, is_fee=True),
        ]
    )
    treasure_request = CoinTransferSignedChangeRequest.create_from_signed_change_request_message(
        message=signed_change_request_message,
        signing_key=treasury_account_key_pair.private,
    )
    blockchain_facade.add_block_from_signed_change_request(treasure_request)
    assert blockchain_facade.get_account_balance(self_node.identifier) == 104

    signed_change_request_message = CoinTransferSignedChangeRequestMessage(
        account_lock=blockchain_facade.get_account_lock(self_node_key_pair.public),
        txs=[
            CoinTransferTransaction(recipient=regular_node.identifier, amount=104),
        ]
    )
    self_request = CoinTransferSignedChangeRequest.create_from_signed_change_request_message(
        message=signed_change_request_message,
        signing_key=self_node_key_pair.private,
    )
    blockchain_facade.add_block_from_signed_change_request(self_request)
    assert blockchain_facade.get_account_balance(self_node.identifier) == 0
    assert blockchain_facade.get_account_balance(regular_node.identifier) == 104


@coin_transfer_message_type_validation_parametrizer
def test_type_validation_for_coin_transfer_message_on_parsing(
    id_,
    account_lock,
    transaction,
    recipient,
    is_fee,
    amount,
    memo,
    search_re,
    expected_response_body,
):
    tx = CoinTransferTransaction(recipient='0' * 64, amount=10, is_fee=True, memo='message')
    serialized = {
        'signer': '0' * 64,
        'signature': '0' * 128,
        'message': {
            'type':
                2,
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
    }
    serialized_json = json.dumps(serialized)
    with pytest.raises(PydanticValidationError) as exc_info:
        SignedChangeRequest.parse_raw(serialized_json)

    assert re.search(search_re, str(exc_info.value), flags=re.DOTALL)

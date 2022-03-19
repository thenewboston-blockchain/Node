import json

import pytest
from django.db import connection

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models.block_confirmation import BlockConfirmation
from node.blockchain.models.block_confirmation import BlockConfirmation as ORMBlockConfirmation


@pytest.mark.usefixtures('rich_blockchain', 'as_confirmation_validator')
def test_send_confirmation_to_cv(confirmation_validator_key_pair_2, api_client):
    assert not ORMBlockConfirmation.objects.exists()

    facade = BlockchainFacade.get_instance()
    assert facade.get_next_block_number() >= 4
    block = facade.get_block_by_number(4)

    hash_ = block.make_hash()
    block_confirmation = BlockConfirmation.create(
        block.get_block_number(), hash_, confirmation_validator_key_pair_2.private
    )
    payload = block_confirmation.json()
    response = api_client.post('/api/block-confirmations/', payload, content_type='application/json')

    assert response.status_code == 201
    confirmation_orm = ORMBlockConfirmation.objects.get_or_none(number=block_confirmation.get_number(), hash=hash_)
    assert confirmation_orm
    assert confirmation_orm.signer == confirmation_validator_key_pair_2.public
    assert confirmation_orm.body == payload


@pytest.mark.usefixtures('rich_blockchain', 'as_confirmation_validator')
def test_confirmation_with_invalid_signature_is_not_accepted(confirmation_validator_key_pair_2, api_client):
    assert not ORMBlockConfirmation.objects.exists()

    facade = BlockchainFacade.get_instance()
    assert facade.get_next_block_number() >= 4
    block = facade.get_block_by_number(4)

    hash_ = block.make_hash()
    block_confirmation = BlockConfirmation.create(
        block.get_block_number(), hash_, confirmation_validator_key_pair_2.private
    )
    payload_dict = block_confirmation.dict()
    payload_dict['signature'] = '0' * 128
    payload = json.dumps(payload_dict)
    response = api_client.post('/api/block-confirmations/', payload, content_type='application/json')

    assert response.status_code == 400
    assert response.json() == {'non_field_errors': [{'code': 'invalid', 'message': 'Invalid signature'}]}

    # This is because we have queried the database and nested transactions (save points) are not supported
    assert connection.needs_rollback
    connection.set_rollback(False)

    assert not ORMBlockConfirmation.objects.exists()

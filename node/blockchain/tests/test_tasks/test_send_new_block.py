from unittest.mock import patch

import pytest

from node.blockchain.facade import BlockchainFacade
from node.blockchain.tasks.send_new_block import send_new_block_task
from node.blockchain.tests.factories.signed_change_request.coin_transfer import (
    make_coin_transfer_signed_change_request
)


@pytest.mark.usefixtures('rich_blockchain')
def test_send_new_block_task(
    treasury_account_key_pair,
    regular_node_key_pair,
    self_node_key_pair,
    primary_validator_key_pair,
    confirmation_validator_node,
    confirmation_validator_node_2,
):
    facade = BlockchainFacade.get_instance()
    block = facade.add_block_from_signed_change_request(
        signed_change_request=make_coin_transfer_signed_change_request(
            sender_key_pair=treasury_account_key_pair,
            recipient_account=regular_node_key_pair.public,
            node_account=self_node_key_pair.public
        ),
        signing_key=primary_validator_key_pair.private,
        validate=False,
    )

    block_number = block.get_block_number()
    with patch('node.core.clients.node.NodeClient.send_block') as mock:
        send_new_block_task(block_number)

    block_json = block.json()
    sorted_call_args_list = sorted((args[0] for args in mock.call_args_list), key=lambda x: x[0].identifier)
    assert sorted_call_args_list == [
        (confirmation_validator_node_2, block_json),
        (confirmation_validator_node, block_json),
    ]

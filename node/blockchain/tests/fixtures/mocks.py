from unittest.mock import patch

import pytest


@pytest.fixture
def mock_get_primary_validator(primary_validator_node):
    with patch('node.blockchain.facade.BlockchainFacade.get_primary_validator', return_value=primary_validator_node):
        yield


@pytest.fixture(autouse=True)
def start_send_new_block_task_mock():
    with patch('node.blockchain.views.signed_change_request.start_send_new_block_task') as mock:
        yield mock


@pytest.fixture(autouse=True)
def start_process_block_confirmations_task_mock():
    with patch('node.blockchain.views.block_confirmation.start_process_block_confirmations_task') as mock:
        yield mock

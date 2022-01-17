from unittest.mock import patch

import pytest


@pytest.fixture
def mock_get_primary_validator(primary_validator_node):
    with patch('node.blockchain.facade.BlockchainFacade.get_primary_validator', return_value=primary_validator_node):
        yield

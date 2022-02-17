import pytest

from node.blockchain.inner_models import AccountState
from node.core.exceptions import ValidationError


@pytest.mark.parametrize('balance, with_node', ((10, False), (None, True)))
def test_serialize_and_deserialize(balance, with_node, self_node):
    node = self_node if with_node else None
    account_state = AccountState(balance=balance, node=node, account_lock='0' * 64)
    serialized = account_state.json()
    deserialized = AccountState.parse_raw(serialized)
    assert account_state.balance == balance
    assert account_state.node == node
    assert account_state.account_lock == '0' * 64
    assert deserialized == account_state

    serialized2 = deserialized.json()
    assert serialized == serialized2


def test_raise_when_both_are_empty():
    with pytest.raises(ValidationError, match='At least one attribute of AccountState should not be empty'):
        AccountState(account_lock='0' * 64)

from dataclasses import dataclass

from .account_state import AccountState


@dataclass
class BlockchainState:
    account_states: dict[str, AccountState]

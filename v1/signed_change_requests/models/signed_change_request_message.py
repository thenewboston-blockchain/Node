from dataclasses import dataclass

from v1.general.models.alpha_account import AlphaAccount


@dataclass
class BaseSignedChangeRequestMessage:
    account_lock: str


@dataclass
class GenesisSignedChangeRequestMessage(BaseSignedChangeRequestMessage):
    accounts: dict[str, AlphaAccount]
    request_type: str = 'GENESIS'

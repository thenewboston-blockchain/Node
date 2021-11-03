from dataclasses import dataclass

from v1.general.models.alpha_account import AlphaAccount


@dataclass
class BaseSignedChangeRequestMessage:
    lock: str
    request_type: str


@dataclass
class GenesisSignedChangeRequestMessage(BaseSignedChangeRequestMessage):
    accounts: dict[str, AlphaAccount]

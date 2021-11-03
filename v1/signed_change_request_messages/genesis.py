from dataclasses import dataclass

from v1.accounts.models.alpha_account import AlphaAccount
from .base import BaseSignedChangeRequestMessage


@dataclass
class GenesisSignedChangeRequestMessage(BaseSignedChangeRequestMessage):
    accounts: dict[str, AlphaAccount]

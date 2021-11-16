from dataclasses import dataclass

from ..alpha_account import AlphaAccount
from .base import BaseSignedChangeRequestMessage


@dataclass
class GenesisSignedChangeRequestMessage(BaseSignedChangeRequestMessage):
    accounts: dict[str, AlphaAccount]

from dataclasses import dataclass

from v1.signed_change_requests.models.genesis import GenesisSignedChangeRequest
from .base import BaseBlockMessage


@dataclass
class GenesisBlockMessage(BaseBlockMessage):
    signed_change_request: GenesisSignedChangeRequest

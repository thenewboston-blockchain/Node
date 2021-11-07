from dataclasses import dataclass

from .base import BaseBlockMessage
from .signed_change_request.genesis import GenesisSignedChangeRequest


@dataclass
class GenesisBlockMessage(BaseBlockMessage):
    signed_change_request: GenesisSignedChangeRequest

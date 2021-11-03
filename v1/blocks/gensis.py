from dataclasses import dataclass

from v1.signed_change_requests.genesis import GenesisSignedChangeRequest
from .base import BaseBlock


@dataclass
class GenesisBlock(BaseBlock):
    signed_change_request: GenesisSignedChangeRequest

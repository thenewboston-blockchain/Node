from dataclasses import dataclass

from v1.signed_change_requests.models.signed_change_request import GenesisSignedChangeRequest
from .base_block import BaseBlock


@dataclass
class GenesisBlock(BaseBlock):
    signed_change_request: GenesisSignedChangeRequest

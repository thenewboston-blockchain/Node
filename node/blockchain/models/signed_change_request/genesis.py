from dataclasses import dataclass

from ..signed import Signed
from ..signed_change_request_message import GenesisSignedChangeRequestMessage


@dataclass
class GenesisSignedChangeRequest(Signed):
    message: GenesisSignedChangeRequestMessage

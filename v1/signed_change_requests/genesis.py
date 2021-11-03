from dataclasses import dataclass

from v1.general.models.signed import Signed
from v1.signed_change_request_messages.genesis import GenesisSignedChangeRequestMessage


@dataclass
class GenesisSignedChangeRequest(Signed):
    message: GenesisSignedChangeRequestMessage

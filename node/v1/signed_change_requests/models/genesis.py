from dataclasses import dataclass

from v1.blockchain.models.signed import Signed
from v1.signed_change_request_messages.models.genesis import GenesisSignedChangeRequestMessage


@dataclass
class GenesisSignedChangeRequest(Signed):
    message: GenesisSignedChangeRequestMessage

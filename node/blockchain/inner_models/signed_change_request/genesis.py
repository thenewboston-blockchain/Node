from typing import TypeVar

from ..signed_change_request import SignedChangeRequest
from ..signed_change_request_message import GenesisSignedChangeRequestMessage

T = TypeVar('T', bound='SignedChangeRequest')


class GenesisSignedChangeRequest(SignedChangeRequest):
    message: GenesisSignedChangeRequestMessage

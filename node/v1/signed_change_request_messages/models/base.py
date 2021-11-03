from dataclasses import dataclass


@dataclass
class BaseSignedChangeRequestMessage:
    lock: str
    request_type: str

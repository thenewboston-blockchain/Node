from dataclasses import dataclass


@dataclass
class Signed:
    signature: str
    signer: str

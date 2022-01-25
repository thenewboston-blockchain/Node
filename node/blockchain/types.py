from enum import IntEnum, unique
from typing import NamedTuple

from pydantic.types import _registered

from node.core.utils.types import hexstr64, hexstr64_i, hexstr128  # noqa: I101


@unique
class Type(IntEnum):
    GENESIS = 0
    NODE_DECLARATION = 1
    COIN_TRANSFER = 2


@unique
class NodeRole(IntEnum):
    PRIMARY_VALIDATOR = 1
    CONFIRMATION_VALIDATOR = 2
    REGULAR_NODE = 3


@_registered
class AccountNumber(hexstr64):
    pass


@_registered
class AlphaAccountNumber(hexstr64_i, AccountNumber):
    pass


@_registered
class Hash(hexstr64):
    pass


@_registered
class AccountLock(Hash):
    pass


@_registered
class AlphaAccountLock(hexstr64_i, AccountLock):
    pass


@_registered
class BlockIdentifier(Hash):
    pass


@_registered
class SigningKey(hexstr64):
    pass


@_registered
class Signature(hexstr128):
    pass


class KeyPair(NamedTuple):
    public: AccountNumber
    private: SigningKey

from enum import IntEnum, unique
from typing import NamedTuple


@unique
class Type(IntEnum):
    GENESIS = 0


class hexstr(str):
    pass


class intstr(str):
    pass


class AccountNumber(hexstr):
    pass


class AccountLock(hexstr):
    pass


class SigningKey(hexstr):
    pass


class BlockIdentifier(hexstr):
    pass


class Hash(hexstr):
    pass


class Signature(hexstr):
    pass


class KeyPair(NamedTuple):
    public: AccountNumber
    private: SigningKey

from enum import IntEnum, unique
from typing import NamedTuple

from pydantic import conint, constr
from pydantic.types import _registered


@unique
class Type(IntEnum):
    GENESIS = 0
    NODE_DECLARATION = 1


hexstr = constr(regex=r'^[0-9a-f]+$', strict=True)

intstr = constr(regex=r'^(?:0|[1-9][0-9]*)$', strict=True)
positive_int = conint(ge=0, strict=True)


class hexstr64(hexstr):  # type: ignore
    min_length = 64
    max_length = 64


class hexstr128(hexstr):  # type: ignore
    min_length = 128
    max_length = 128


@_registered
class AccountNumber(hexstr64):
    pass


@_registered
class Hash(hexstr64):
    pass


@_registered
class AccountLock(Hash):
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

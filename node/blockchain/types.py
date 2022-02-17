from enum import IntEnum, unique
from typing import NamedTuple

from pydantic.errors import AnyStrMaxLengthError, AnyStrMinLengthError
from pydantic.types import _registered

from node.core.utils.types import hexstr64, hexstr64_i, hexstr128  # noqa: I101


@unique
class Type(IntEnum):
    GENESIS = 0
    NODE_DECLARATION = 1
    COIN_TRANSFER = 2
    PV_SCHEDULE_UPDATE = 3


@unique
class NodeRole(IntEnum):
    PRIMARY_VALIDATOR = 1
    CONFIRMATION_VALIDATOR = 2
    REGULAR_NODE = 3


@_registered
class AccountNumber(hexstr64):

    @classmethod
    def resemble_constr_length_validator(cls, value):
        value_len = len(value)

        min_length = cls.min_length
        if min_length is not None and value_len < min_length:
            raise AnyStrMinLengthError(limit_value=min_length)

        max_length = cls.max_length
        if max_length is not None and value_len > max_length:
            raise AnyStrMaxLengthError(limit_value=max_length)

        return value

    @classmethod
    def validate(cls, value):
        value = super().validate(value)
        # We need resemble_constr_length_validator() to use standalone AccountNumber() validation
        return cls.resemble_constr_length_validator(value)


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

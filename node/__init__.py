from enum import IntEnum


def patch_pydantic():
    from pydantic.validators import _VALIDATORS, enum_member_validator, int_validator, strict_int_validator
    assert _VALIDATORS[0][0] is IntEnum
    assert _VALIDATORS[0][1] == [int_validator, enum_member_validator]
    _VALIDATORS[0] = (IntEnum, [strict_int_validator, enum_member_validator])


patch_pydantic()

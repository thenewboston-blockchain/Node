from pydantic import conint, constr

hexstr = constr(regex=r'^[0-9a-f]+$', strict=True)
hexstr_i = constr(regex=r'^[0-9a-fA-F]+$', strict=True)  # case-insensitive hexstr

intstr = constr(regex=r'^(?:0|[1-9][0-9]*)$', strict=True)
positive_int_with_zero = conint(ge=0, strict=True)
positive_int = conint(gt=0, strict=True)


class hexstr64(hexstr):  # type: ignore
    min_length = 64
    max_length = 64


class hexstr64_i(hexstr_i):  # type: ignore
    min_length = 64
    max_length = 64


class hexstr128(hexstr):  # type: ignore
    min_length = 128
    max_length = 128

import yaml

from .types import hexstr


def yaml_coerce(value):
    if isinstance(value, str):
        return yaml.load('dummy: ' + value, Loader=yaml.SafeLoader)['dummy']

    return value


def hex_to_bytes(hex_string: hexstr) -> bytes:
    return bytes.fromhex(hex_string)


def bytes_to_hex(bytes_: bytes) -> hexstr:
    return hexstr(bytes(bytes_).hex())


def set_if_not_none(dict_, key, value):
    if value is not None:
        dict_[key] = value

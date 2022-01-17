from . import Block

TYPE_MAP = {}

for subclass in Block.__subclasses__():
    key = subclass.__fields__['message'].type_.__fields__['type'].default
    assert key is not None
    TYPE_MAP[key] = subclass


def get_block_subclass(type_):
    return TYPE_MAP[type_]


def get_block_message_subclass(type_):
    return get_block_subclass(type_).__fields__['message'].type_


def get_signed_change_request_subclass(type_):
    return get_block_message_subclass(type_).__fields__['request'].type_

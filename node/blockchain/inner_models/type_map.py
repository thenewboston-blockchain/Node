from . import BlockMessage

TYPE_MAP = {}

for subclass in BlockMessage.__subclasses__():
    key = subclass.__fields__['type'].default
    assert key is not None
    TYPE_MAP[key] = subclass


def get_block_message_subclass(type_):
    return TYPE_MAP[type_]


def get_signed_change_request_subclass(type_):
    return TYPE_MAP[type_].__fields__['request'].type_

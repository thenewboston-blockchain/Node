from collections.abc import Sequence
from typing import Any

from node.core.exceptions import NotEnoughNestingError

from .misc import SENTINEL


def deep_update(base_dict, update_with):
    for key, value in update_with.items():
        if isinstance(value, dict):
            base_dict_value = base_dict.get(key)
            if isinstance(base_dict_value, dict):
                deep_update(base_dict_value, value)
            else:
                base_dict[key] = value
        else:
            base_dict[key] = value

    return base_dict


def deep_get(source: dict, keys: Sequence[str]):
    # TODO(dmu) LOW: Reimplement with reduce() for higher performance if needed:
    #                https://stackoverflow.com/questions/25833613/safe-method-to-get-value-of-nested-dictionary
    value: Any = source
    for key in keys[:-1]:
        value = value.get(key)
        if not isinstance(value, dict):
            raise NotEnoughNestingError('Not enough nesting')

    return value[keys[-1]]


def deep_set(target: dict, keys: Sequence[str], value):
    for key in keys[:-1]:
        new_target = target.get(key, SENTINEL)
        if new_target is SENTINEL:
            target[key] = new_target = {}
        elif not isinstance(new_target, dict):
            raise NotEnoughNestingError('Not enough nesting')

        target = new_target

    target[keys[-1]] = value

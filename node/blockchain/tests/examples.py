import functools
import json
import logging
import os
from pathlib import Path

from django.conf import settings

logger = logging.getLogger(__name__)

EXAMPLES_DIR = os.path.join(Path(__file__).resolve().parent, 'examples')


def save_example(file_name, data):
    if not settings.IN_DOCKER:
        with open(get_example_path(file_name), 'w') as fp:
            json.dump(data, fp)


def save_response_as_example(file_name):

    def save(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            data = func(*args, **kwargs)
            assert data is not None

            save_example(file_name, data)

            return data

        return wrapper

    return save


def load_example(file_name):
    path = get_example_path(file_name)

    if not os.path.exists(path):
        logger.warning("%s example file doesn't exist: %s", file_name, path)
        return {}

    with open(path) as fp:
        return json.load(fp)


def get_example_path(file_name):
    return os.path.join(EXAMPLES_DIR, f'{file_name}.json')

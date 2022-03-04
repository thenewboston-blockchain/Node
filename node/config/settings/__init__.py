import logging
import os.path
from pathlib import Path

from split_settings.tools import include, optional

from node.core.utils.pytest import is_pytest_running

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

ENVVAR_SETTINGS_PREFIX = 'TNB_'

LOCAL_SETTINGS_PATH = os.getenv(f'{ENVVAR_SETTINGS_PREFIX}LOCAL_SETTINGS_PATH')
if not LOCAL_SETTINGS_PATH:
    # We dedicate local/settings.unittests.py to have reproducible unittest runs
    LOCAL_SETTINGS_PATH = f'local/settings{".unittests" if is_pytest_running() else ".dev"}.py'

if not os.path.isabs(LOCAL_SETTINGS_PATH):
    LOCAL_SETTINGS_PATH = str(BASE_DIR / LOCAL_SETTINGS_PATH)

# yapf: disable
include(
    'base.py',
    'logging.py',
    'rest_framework.py',
    'celery.py',
    'custom.py',
    optional(LOCAL_SETTINGS_PATH),
    'envvars.py',
    'sentry.py',
    'docker.py',
)
# yapf: enable

logging.captureWarnings(True)

assert SECRET_KEY is not NotImplemented  # type: ignore # noqa: F821
assert NODE_SIGNING_KEY is not NotImplemented  # type: ignore # noqa: F821

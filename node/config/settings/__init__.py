import logging
import os
from pathlib import Path

from split_settings.tools import include, optional
from dotenv import load_dotenv

from node.core.utils.pytest import is_pytest_running

load_dotenv(override=True)

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
ENVVAR_SETTINGS_PREFIX = 'NODE_'

LOCAL_SETTINGS_PATH = os.getenv(f'{ENVVAR_SETTINGS_PREFIX}LOCAL_SETTINGS_PATH')
if not LOCAL_SETTINGS_PATH:
    # We use dedicated local settings here to have reproducible unittest runs
    _suffix = '.unittests' if is_pytest_running() else '.dev'
    LOCAL_SETTINGS_PATH = str(ROOT_DIR / f'local/settings{_suffix}.py')

# yapf: disable
include(
    'base.py',
    'logging.py',
    'rest_framework.py',
    'celery.py',
    'custom.py',
    optional(LOCAL_SETTINGS_PATH),
    'envvars.py',
)
# yapf: enable

logging.captureWarnings(True)

assert SECRET_KEY is not NotImplemented  # type: ignore # noqa: F821

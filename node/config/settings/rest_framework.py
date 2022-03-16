import os
from pathlib import Path

import toml

REST_FRAMEWORK = {
    'DEFAULT_PARSER_CLASSES': ('rest_framework.parsers.JSONParser',),
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'EXCEPTION_HANDLER': 'node.core.exceptions.custom_exception_handler',
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# TODO(dmu) LOW: Do we really need reading from `pyproject.toml`?
pyproject = toml.load(os.path.join(Path(__file__).parent.parent.parent.parent, 'pyproject.toml'))
poetry_section = pyproject['tool']['poetry']
SPECTACULAR_SETTINGS = {
    'TITLE': poetry_section['name'],
    'DESCRIPTION': poetry_section['description'],
    'VERSION': poetry_section['version'],
    'CONTACT': ', '.join(poetry_section['authors']),
    'EXTERNAL_DOCS': 'https://developer.thenewboston.com/',
}

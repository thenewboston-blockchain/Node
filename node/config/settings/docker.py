import os

IN_DOCKER = str(os.getenv(f'{ENVVAR_SETTINGS_PREFIX}IN_DOCKER')).lower() in ['true', '1']  # type: ignore # noqa: F821
if IN_DOCKER or os.path.isfile('/.dockerenv'):
    # We need it to serve static files with DEBUG=False
    assert MIDDLEWARE[:1] == [  # type: ignore # noqa: F821
        'django.middleware.security.SecurityMiddleware'
    ]
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')  # type: ignore # noqa: F821
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

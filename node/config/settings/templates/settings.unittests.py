# mypy: ignore-errors

DEBUG = True

SECRET_KEY = 'django-insecure-^m3d4yj1zic931t3z_b()(xz-_34c3sjeh_4v41rf-2j8qs'

MIDDLEWARE += ('node.core.middleware.LoggingMiddleware',)
LOGGING['formatters']['colored'] = {
    '()': 'node.core.utils.formatters.TracebackSuppressingColoredFormatter',
    'format': '%(log_color)s%(asctime)s %(levelname)s %(name)s %(bold_white)s%(message)s',
}
LOGGING['loggers']['node']['level'] = 'DEBUG'
LOGGING['handlers']['console']['level'] = 'DEBUG'
LOGGING['handlers']['console']['formatter'] = 'colored'

DATABASES['default']['CLIENT']['serverSelectionTimeoutMS'] = 1000
DATABASES['default']['CLIENT']['connectTimeoutMS'] = 1000

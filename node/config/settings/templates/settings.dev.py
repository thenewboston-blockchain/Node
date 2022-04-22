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

NODE_SIGNING_KEY = 'a37e2836805975f334108b55523634c995bd2a4db610062f404510617e83126f'
NODE_SCHEDULE_CAPACITY = 20

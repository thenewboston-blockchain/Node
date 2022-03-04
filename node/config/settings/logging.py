LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            '()': 'node.core.utils.formatters.TracebackSuppressingFormatter',
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s'
        },
    },
    'filters': {
        'sentry': {
            '()': 'node.core.logging.SentryFilter'
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'filters': [],
        },
        'pre_sentry_handler': {
            'level': 'DEBUG',
            'class': 'node.core.logging.FilteringNullHandler',
            'filters': ['sentry'],
        }
    },
    'loggers': {
        logger_name: {
            'level': 'WARNING',
            'propagate': True,
        } for logger_name in (
            'django', 'django.request', 'django.db.backends', 'django.template', 'node', 'node.core.logging',
            'urllib3', 'asyncio', 'djongo'
        )
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console'],
    }
}

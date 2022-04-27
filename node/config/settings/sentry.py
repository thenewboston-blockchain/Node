import os

SENTRY_MAX_STRING_LENGTH = 4096

if not SENTRY_DSN:  # type: ignore # noqa: F821
    SENTRY_DSN = os.getenv('SENTRY_DSN')

if SENTRY_DSN:
    import logging

    import sentry_sdk
    from sentry_sdk import utils
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration

    utils.MAX_STRING_LENGTH = SENTRY_MAX_STRING_LENGTH

    handlers = LOGGING['root']['handlers']  # type: ignore # noqa: F821
    if 'pre_sentry_handler' not in handlers:
        handlers.append('pre_sentry_handler')

    console_handler_filters = LOGGING['handlers']['console']['filters']  # type: ignore # noqa: F821
    if 'sentry' not in console_handler_filters:
        console_handler_filters.append('sentry')

    logging_integration = LoggingIntegration(
        level=logging.DEBUG,  # Breadcrumbs level
        event_level=SENTRY_EVENT_LEVEL,  # type: ignore # noqa: F821
    )

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        debug=True,
        send_default_pii=True,
        # TODO(dmu) HIGH: Provide `release=...`,
        request_bodies='medium',
        integrations=(logging_integration, DjangoIntegration(), CeleryIntegration()),
    )

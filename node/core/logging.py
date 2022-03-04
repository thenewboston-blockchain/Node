import logging


class SentryFilter(logging.Filter):

    def filter(self, record):  # noqa: A003
        if record.levelno >= logging.WARNING and getattr(record, 'exc_info', None) is None:
            # TODO(dmu) MEDIUM: This hack leads to "NoneType: None" being printed along with
            #                   warning messages. Figure out a better solution.
            record.exc_info = (None, None, None)  # trigger Sentry to dump stack trace

        return True


class FilteringNullHandler(logging.NullHandler):

    def handle(self, record):
        return self.filter(record)

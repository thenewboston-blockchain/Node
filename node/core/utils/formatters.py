from logging import WARNING, Formatter  # noqa: I101

from colorlog import ColoredFormatter
from django.conf import settings


class TracebackSuppressingMixin:

    def format(self, record):  # noqa: A003
        if record.levelno > WARNING or not settings.SUPPRESS_WARNINGS_TB:
            return super().format(record)

        record.message = record.getMessage()
        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)

        return self.formatMessage(record)


class TracebackSuppressingFormatter(TracebackSuppressingMixin, Formatter):
    pass


class TracebackSuppressingColoredFormatter(TracebackSuppressingMixin, ColoredFormatter):
    pass

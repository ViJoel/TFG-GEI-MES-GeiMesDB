import logging

from log.logger_config import SUCCESS
from log.logger_config import setup_logging as sl


class AppLogger:
    def __init__(self, name: str):
        self._logger = logging.getLogger(name)

    def _log(self, level, msg, *args, **kwargs):
        self._logger.log(level, msg, *args, **kwargs)

    # =====================
    # Custom level
    # =====================

    def success(self, msg, *args, **kwargs):
        self._log(SUCCESS, msg, *args, **kwargs)

    # =====================
    # Standard levels
    # =====================

    def critical(self, msg, *args, **kwargs):
        self._log(logging.CRITICAL, msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self._log(logging.DEBUG, msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._log(logging.ERROR, msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        self._logger.exception(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self._log(logging.INFO, msg, *args, **kwargs)

    def isEnabledFor(self, level):
        return self._logger.isEnabledFor(level)

    def log(self, level, msg, *args, **kwargs):
        self._logger.log(level, msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._log(logging.WARNING, msg, *args, **kwargs)


def get_logger(name: str):
    return AppLogger(name)


def setup_logging(
    base_dir: str | None = None,
) -> None:
    sl(base_dir)

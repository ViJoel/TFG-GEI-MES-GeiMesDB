import logging
from unittest.mock import MagicMock

import pytest

from log.app_logger import AppLogger, get_logger, setup_logging
from log.logger_config import SUCCESS

# =============================================================================
# FIXTURE LOGGER REAL (mockeado internamente)
# =============================================================================


@pytest.fixture
def logger():
    """
    Crea una instancia de AppLogger con el logger interno parcheado.
    """

    app_logger = AppLogger("test.logger")

    mock = MagicMock()
    app_logger._logger = mock  # sustituimos el logger real por mock

    return app_logger, mock


# =============================================================================
# SUCCESS LOGGING
# =============================================================================


def test_success_logs_correct_level(logger):
    """
    Verifica que success usa el nivel correcto.
    """

    app_logger, mock = logger

    app_logger.success("hello")

    mock.log.assert_called_once_with(SUCCESS, "hello")


def test_success_passes_args_and_kwargs(logger):
    """
    Verifica que success propaga args y kwargs.
    """

    app_logger, mock = logger

    app_logger.success("hello %s", "world", extra={"key": "value"})

    mock.log.assert_called_once_with(
        SUCCESS,
        "hello %s",
        "world",
        extra={"key": "value"},
    )


# =============================================================================
# CRITICAL
# =============================================================================


def test_critical_logs_correct_level(logger):
    """
    Verifica que critical usa el nivel CRITICAL correctamente.
    """

    app_logger, mock = logger

    app_logger.critical("critical message")

    mock.log.assert_called_once_with(
        logging.CRITICAL,
        "critical message",
    )


# =============================================================================
# DEBUG
# =============================================================================


def test_debug_logs_correct_level(logger):
    """
    Verifica que debug usa el nivel DEBUG.
    """

    app_logger, mock = logger

    app_logger.debug("debug message")

    mock.log.assert_called_once_with(logging.DEBUG, "debug message")


# =============================================================================
# ERROR
# =============================================================================


def test_error_logs_correct_level(logger):
    """
    Verifica que error usa el nivel ERROR.
    """

    app_logger, mock = logger

    app_logger.error("error message")

    mock.log.assert_called_once_with(logging.ERROR, "error message")


# =============================================================================
# INFO
# =============================================================================


def test_info_logs_correct_level(logger):
    """
    Verifica que info usa el nivel INFO.
    """

    app_logger, mock = logger

    app_logger.info("info message")

    mock.log.assert_called_once_with(logging.INFO, "info message")


# =============================================================================
# WARNING
# =============================================================================


def test_warning_logs_correct_level(logger):
    """
    Verifica que warning usa el nivel WARNING.
    """

    app_logger, mock = logger

    app_logger.warning("warning message")

    mock.log.assert_called_once_with(logging.WARNING, "warning message")


# =============================================================================
# GET LOGGER FACTORY
# =============================================================================


def test_get_logger_returns_wrapper():
    """
    Verifica que get_logger devuelve instancia de AppLogger.
    """

    logger = get_logger("test.name")

    assert isinstance(logger, AppLogger)


# =============================================================================
# SETUP LOGGING WRAPPER
# =============================================================================


def test_setup_logging_delegates(monkeypatch):
    """
    Verifica que setup_logging delega correctamente a logger_config.
    """

    mock_setup = MagicMock()

    monkeypatch.setattr(
        "log.app_logger.sl",
        mock_setup,
    )

    setup_logging("/tmp")

    mock_setup.assert_called_once_with("/tmp")

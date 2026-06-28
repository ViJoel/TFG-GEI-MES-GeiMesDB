from sqlite3 import IntegrityError, OperationalError
from unittest.mock import patch

import pytest

from modules.database.wrapper import handle_db_errors

# =============================================================================
# handle_db_errors
# =============================================================================


def test_handle_db_errors_integrity():
    """
    Verifica que el decorador handle_db_errors captura
    correctamente errores de integridad (IntegrityError)
    y registra un warning en el logger.
    """

    @handle_db_errors("insert test")
    def func():
        raise IntegrityError("duplicate key")

    with patch("logging.Logger.warning") as mock_log:
        with pytest.raises(IntegrityError):
            func()

    mock_log.assert_called_once()


def test_handle_db_errors_operational():
    """
    Verifica que el decorador handle_db_errors captura
    errores operacionales de SQLite (OperationalError)
    y registra un error en el logger.
    """

    @handle_db_errors("query test")
    def func():
        raise OperationalError("db locked")

    with patch("logging.Logger.error") as mock_log:
        with pytest.raises(OperationalError):
            func()

    mock_log.assert_called_once()


def test_handle_db_errors_generic_exception():
    """
    Verifica que el decorador handle_db_errors captura
    excepciones genéricas no controladas y las registra
    como error en el logger.
    """

    @handle_db_errors("unknown op")
    def func():
        raise Exception("boom")

    with patch("logging.Logger.error") as mock_log:
        with pytest.raises(Exception):
            func()

    mock_log.assert_called_once()

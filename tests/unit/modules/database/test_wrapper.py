from sqlite3 import IntegrityError, OperationalError
from unittest.mock import patch

import pytest

from modules.database.wrapper import handle_db_errors


def test_handle_db_errors_integrity():
    @handle_db_errors("insert test")
    def func():
        raise IntegrityError("duplicate key")

    with patch("logging.Logger.warning") as mock_log:
        with pytest.raises(IntegrityError):
            func()

    mock_log.assert_called_once()


def test_handle_db_errors_operational():
    @handle_db_errors("query test")
    def func():
        raise OperationalError("db locked")

    with patch("logging.Logger.error") as mock_log:
        with pytest.raises(OperationalError):
            func()

    mock_log.assert_called_once()


def test_handle_db_errors_generic_exception():
    @handle_db_errors("unknown op")
    def func():
        raise Exception("boom")

    with patch("logging.Logger.error") as mock_log:
        with pytest.raises(Exception):
            func()

    mock_log.assert_called_once()

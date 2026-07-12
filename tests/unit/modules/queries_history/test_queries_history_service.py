from datetime import datetime
from unittest.mock import MagicMock

from entities.connection import Connection
from entities.driver import Driver
from entities.queries_history_entry import QueriesHistoryEntry
from modules.queries_history import service


# =============================================================================
# FIXTURES
# =============================================================================

def create_connection():

    return Connection(
        id="1",
        name="SQLite",
        driver=Driver.SQLITE,
        path="/tmp/test.db",
    )


# =============================================================================
# save_queries_history_batch
# =============================================================================


def test_save_queries_history_batch(monkeypatch):
    """
    Debe delegar la inserción en la capa de modelo.
    """

    connection = create_connection()

    entries = [
        QueriesHistoryEntry(
            connection_id="1",
            query="SELECT 1",
            executed_at=datetime.now(),
        )
    ]

    mock = MagicMock()

    monkeypatch.setattr(
        service,
        "sqhb",
        mock,
    )

    service.save_queries_history_batch(
        connection,
        entries,
    )

    mock.assert_called_once_with(
        connection=connection,
        entries=entries,
    )


# =============================================================================
# get_queries_history
# =============================================================================


def test_get_queries_history(monkeypatch):
    """
    Debe delegar la consulta en la capa de modelo
    y devolver su resultado.
    """

    connection = create_connection()

    start = datetime(2024, 1, 1)
    end = datetime(2024, 12, 31)

    expected = [
        QueriesHistoryEntry(
            connection_id="1",
            query="SELECT 1",
            executed_at=datetime.now(),
        )
    ]

    mock = MagicMock(return_value=expected)

    monkeypatch.setattr(
        service,
        "gqh",
        mock,
    )

    result = service.get_queries_history(
        connection,
        start,
        end,
    )

    assert result is expected

    mock.assert_called_once_with(
        connection=connection,
        start=start,
        end=end,
    )

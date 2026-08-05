import sqlite3
from datetime import (
    datetime,
    timedelta,
)

import pytest

from entities.connection import Connection
from entities.driver import Driver
from entities.queries_history_entry import QueriesHistoryEntry
from modules.queries_history.model import (
    _map_row_to_entry,
    get_queries_history,
    save_queries_history_batch,
)

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def sqlite_db(tmp_path, monkeypatch):
    """
    Crea una base de datos SQLite temporal y
    sustituye la conexión real del módulo.
    """

    db = tmp_path / "test.db"

    with sqlite3.connect(db) as conn:
        conn.execute("""
        CREATE TABLE queries_history (
            connection_id TEXT,
            query TEXT,
            executed_at TEXT
        )
        """)
        conn.commit()

    def fake_get_connection():

        conn = sqlite3.connect(db)
        conn.row_factory = sqlite3.Row
        return conn

    monkeypatch.setattr(
        "modules.queries_history.model.get_db_connection",
        fake_get_connection,
    )

    return db


def create_connection():

    return Connection(
        id="1",
        name="SQLite",
        driver=Driver.SQLITE,
        path="/tmp/test.db",
    )


# =============================================================================
# _map_row_to_entry
# =============================================================================


def test_map_row_to_entry(sqlite_db):
    """
    Verifica que una fila SQLite se transforma
    correctamente en un QueriesHistoryEntry.
    """

    now = datetime.now().replace(microsecond=0)

    with sqlite3.connect(sqlite_db) as conn:

        conn.row_factory = sqlite3.Row

        conn.execute(
            """
            INSERT INTO queries_history
            VALUES (?, ?, ?)
            """,
            (
                "1",
                "SELECT 1",
                now.isoformat(),
            ),
        )

        conn.commit()

        row = conn.execute("SELECT * FROM queries_history").fetchone()

    result = _map_row_to_entry(row)

    assert isinstance(result, QueriesHistoryEntry)
    assert result.connection_id == "1"
    assert result.query == "SELECT 1"
    assert result.executed_at == now


# =============================================================================
# save_queries_history_batch
# =============================================================================


def test_save_queries_history_batch(sqlite_db):
    """
    Comprueba que todas las entradas se insertan
    correctamente mediante executemany().
    """

    connection = create_connection()

    now = datetime.now()

    entries = [
        QueriesHistoryEntry(
            connection_id="1",
            query="SELECT 1",
            executed_at=now,
        ),
        QueriesHistoryEntry(
            connection_id="1",
            query="SELECT 2",
            executed_at=now + timedelta(seconds=1),
        ),
    ]

    save_queries_history_batch(
        connection,
        entries,
    )

    with sqlite3.connect(sqlite_db) as conn:

        conn.row_factory = sqlite3.Row

        rows = conn.execute("""
            SELECT connection_id, query
            FROM queries_history
            ORDER BY query
        """).fetchall()

    assert len(rows) == 2
    assert rows[0]["query"] == "SELECT 1"
    assert rows[1]["query"] == "SELECT 2"


def test_save_queries_history_batch_empty(sqlite_db):
    """
    Insertar una lista vacía no debe producir
    errores ni insertar registros.
    """

    connection = create_connection()

    save_queries_history_batch(
        connection,
        [],
    )

    with sqlite3.connect(sqlite_db) as conn:

        count = conn.execute("SELECT COUNT(*) FROM queries_history").fetchone()[0]

    assert count == 0


# =============================================================================
# get_queries_history
# =============================================================================


def test_get_queries_history(sqlite_db):
    """
    Comprueba que recupera correctamente las
    entradas ordenadas por fecha descendente.
    """

    connection = create_connection()

    now = datetime.now()

    with sqlite3.connect(sqlite_db) as conn:

        conn.executemany(
            """
            INSERT INTO queries_history
            VALUES (?, ?, ?)
            """,
            [
                (
                    "1",
                    "SELECT 1",
                    now.isoformat(),
                ),
                (
                    "1",
                    "SELECT 2",
                    (now + timedelta(seconds=1)).isoformat(),
                ),
            ],
        )

        conn.commit()

    result = get_queries_history(
        connection,
        start=now - timedelta(days=1),
        end=now + timedelta(days=1),
    )

    assert len(result) == 2

    # ORDER BY ASC
    assert result[0].query == "SELECT 1"
    assert result[1].query == "SELECT 2"


def test_get_queries_history_filters_connection_and_dates(sqlite_db):
    """
    Debe devolver únicamente las entradas
    correspondientes a la conexión y rango
    de fechas solicitados.
    """

    connection = create_connection()

    now = datetime.now()

    with sqlite3.connect(sqlite_db) as conn:

        conn.executemany(
            """
            INSERT INTO queries_history
            VALUES (?, ?, ?)
            """,
            [
                (
                    "1",
                    "SELECT ok",
                    now.isoformat(),
                ),
                (
                    "2",
                    "SELECT other connection",
                    now.isoformat(),
                ),
                (
                    "1",
                    "SELECT old",
                    (now - timedelta(days=10)).isoformat(),
                ),
            ],
        )

        conn.commit()

    result = get_queries_history(
        connection,
        start=now - timedelta(days=1),
        end=now + timedelta(days=1),
    )

    assert len(result) == 1
    assert result[0].query == "SELECT ok"


def test_get_queries_history_empty(sqlite_db):
    """
    Si no existen registros, debe devolver
    una lista vacía.
    """

    connection = create_connection()

    result = get_queries_history(
        connection,
        start=datetime.now() - timedelta(days=1),
        end=datetime.now() + timedelta(days=1),
    )

    assert result == []

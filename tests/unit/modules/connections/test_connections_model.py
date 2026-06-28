import logging
import sqlite3

import pytest

from entities.connection import Connection
from entities.driver import Driver
from modules.connections.model import (
    _map_row_to_connection,
    connection_exists,
    create_connection,
    delete_connection,
    get_all_connections,
    update_connection,
)

# =============================================================================
# FIXTURE LOCAL: DB + MONKEYPATCH + LOGGER
# =============================================================================


@pytest.fixture
def sqlite_db(tmp_path, monkeypatch):
    """
    Crea una base de datos SQLite temporal para tests y
    parchea la conexión real del módulo por una local.
    """

    db = tmp_path / "test.db"

    with sqlite3.connect(db) as conn:
        conn.execute("""
        CREATE TABLE connections (
            id TEXT PRIMARY KEY,
            name TEXT,
            driver TEXT,
            host TEXT,
            port INTEGER,
            database TEXT,
            username TEXT,
            password TEXT,
            path TEXT
        )
        """)
        conn.commit()

    def fake_get_connection():
        """
        Devuelve conexión SQLite apuntando a la DB de test.
        """

        conn = sqlite3.connect(db)
        conn.row_factory = sqlite3.Row
        return conn

    monkeypatch.setattr(
        "modules.connections.model.get_db_connection", fake_get_connection
    )

    return db


@pytest.fixture(autouse=True)
def patch_logger_success(monkeypatch):
    """
    Evita errores si el código usa
    logger.success (no estándar en logging).

    Se redirige a logger.info.
    """

    logger = logging.getLogger("modules.connections.model")
    monkeypatch.setattr(logger, "success", logger.info, raising=False)


# =============================================================================
# _map_row_to_connection
# =============================================================================


def test_map_row_to_connection(sqlite_db):
    """
    Verifica que una fila SQLite se transforma
    correctamente en un objeto Connection.
    """

    with sqlite3.connect(sqlite_db) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute(
            "INSERT INTO connections VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("1", "Local", "sqlite", None, None, None, None, None, "/tmp.db"),
        )
        conn.commit()

        row = conn.execute("SELECT * FROM connections").fetchone()

    result = _map_row_to_connection(row)

    assert isinstance(result, Connection)
    assert result.id == "1"
    assert result.name == "Local"
    assert result.driver == Driver.SQLITE


# =============================================================================
# create_connection
# =============================================================================


def test_create_connection(sqlite_db):
    """
    Comprueba que se inserta correctamente
    una conexión en la base de datos.
    """

    conn_obj = Connection(
        id="1",
        name="Local",
        driver=Driver.SQLITE,
        path="/tmp.db",
    )

    create_connection(conn_obj)

    with sqlite3.connect(sqlite_db) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM connections WHERE id='1'").fetchone()

    assert row is not None
    assert row["name"] == "Local"


# =============================================================================
# update_connection
# =============================================================================


def test_update_connection(sqlite_db):
    """
    Comprueba que una conexión existente
    se actualiza correctamente.
    """

    with sqlite3.connect(sqlite_db) as conn:
        conn.execute(
            "INSERT INTO connections VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("1", "Old", "sqlite", None, None, None, None, None, "/tmp.db"),
        )
        conn.commit()

    conn_obj = Connection(
        id="1",
        name="Updated",
        driver=Driver.SQLITE,
        path="/tmp.db",
    )

    update_connection(conn_obj)

    with sqlite3.connect(sqlite_db) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT name FROM connections WHERE id='1'").fetchone()

    assert row["name"] == "Updated"


def test_update_connection_when_not_exists(sqlite_db):
    """
    Si intentas actualizar una conexión que no existe,
    no debe romper y no debe crear registros.
    """

    conn_obj = Connection(
        id="999",
        name="DoesNotExist",
        driver=Driver.SQLITE,
        path="/tmp.db",
    )

    update_connection(conn_obj)

    with sqlite3.connect(sqlite_db) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM connections WHERE id='999'").fetchone()

    assert row is None


# =============================================================================
# delete_connection
# =============================================================================


def test_delete_connection(sqlite_db):
    """
    Comprueba que una conexión
    se elimina correctamente.
    """

    with sqlite3.connect(sqlite_db) as conn:
        conn.execute(
            "INSERT INTO connections VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("1", "Local", "sqlite", None, None, None, None, None, "/tmp.db"),
        )
        conn.commit()

    conn_obj = Connection(id="1")

    delete_connection(conn_obj)

    with sqlite3.connect(sqlite_db) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM connections WHERE id='1'").fetchone()

    assert row is None


def test_delete_connection_when_not_exists(sqlite_db):
    """
    Si intentas borrar una conexión inexistente,
    no debe lanzar error ni afectar la base de datos.
    """

    conn_obj = Connection(id="999")

    delete_connection(conn_obj)

    with sqlite3.connect(sqlite_db) as conn:
        row = conn.execute("SELECT * FROM connections WHERE id='999'").fetchone()

    assert row is None


# =============================================================================
# connection_exists
# =============================================================================


def test_connection_exists_true(sqlite_db):
    """
    Comprueba que connection_exists
    devuelve True si existe la conexión.
    """

    with sqlite3.connect(sqlite_db) as conn:
        conn.execute(
            "INSERT INTO connections VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("1", "Local", "sqlite", None, None, None, None, None, "/tmp.db"),
        )
        conn.commit()

    assert connection_exists("1") is True


def test_connection_exists_false(sqlite_db):
    """
    Comprueba que connection_exists
    devuelve False si no existe la
    conexión.
    """

    assert connection_exists("does-not-exist") is False


# =============================================================================
# get_all_connections
# =============================================================================


def test_get_all_connections(sqlite_db):
    """
    Comprueba que se devuelven todas
    las conexiones ordenadas correctamente.
    """

    with sqlite3.connect(sqlite_db) as conn:
        conn.executemany(
            "INSERT INTO connections VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                ("2", "B", "sqlite", None, None, None, None, None, "/tmp.db"),
                ("1", "A", "sqlite", None, None, None, None, None, "/tmp.db"),
            ],
        )
        conn.commit()

    result = get_all_connections()

    assert len(result) == 2
    assert result[0].name == "A"
    assert result[1].name == "B"

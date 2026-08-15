import sqlite3

import pytest

from entities.connection import Connection
from entities.driver import Driver
from modules.connections.crypto import encrypt
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
            port TEXT,
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


def test_create_sqlite_connection(sqlite_db):
    """
    Comprueba que se inserta correctamente
    una conexión SQLite en la base de datos.
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
        row = conn.execute(
            "SELECT * FROM connections WHERE id = ?",
            ("1",),
        ).fetchone()

    assert row is not None
    assert row["name"] == "Local"


def test_create_network_connection(sqlite_db):
    """
    Comprueba que se inserta correctamente
    una conexión con driver de red en la
    base de datos.
    """

    conn_obj = Connection(
        id="1",
        name="Remote",
        driver=Driver.POSTGRESQL,
        host="localhost",
        port=5432,
        database="test_db",
        username="postgres",
        password="secret",
    )

    create_connection(conn_obj)

    with sqlite3.connect(sqlite_db) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM connections WHERE id = ?",
            ("1",),
        ).fetchone()

    assert row is not None
    assert row["name"] == "Remote"


@pytest.mark.parametrize(
    ("connection", "encrypted_fields"),
    [
        (
            Connection(
                id="sqlite",
                name="SQLite",
                driver=Driver.SQLITE,
                path="/tmp/test.db",
            ),
            {
                "path": "/tmp/test.db",
            },
        ),
        (
            Connection(
                id="postgres",
                name="PostgreSQL",
                driver=Driver.POSTGRESQL,
                host="localhost",
                port=5432,
                database="my_db",
                username="postgres",
                password="secret",
            ),
            {
                "host": "localhost",
                "port": "5432",
                "database": "my_db",
                "username": "postgres",
                "password": "secret",
            },
        ),
    ],
)
def test_create_connection_stores_sensitive_data_encrypted(
    sqlite_db,
    connection: Connection,
    encrypted_fields: dict[str, str],
):
    """
    Comprueba que los datos sensibles se almacenan
    cifrados en la base de datos, mientras que los
    campos no sensibles permanecen en texto plano.
    """

    create_connection(connection)

    with sqlite3.connect(sqlite_db) as conn:
        conn.row_factory = sqlite3.Row

        row = conn.execute(
            "SELECT * FROM connections WHERE id = ?",
            (connection.id,),
        ).fetchone()

    assert row is not None

    # Campos no sensibles.
    assert row["id"] == connection.id
    assert row["name"] == connection.name
    assert row["driver"] == connection.driver.value

    # Campos sensibles.
    for field, plain_value in encrypted_fields.items():
        assert row[field] != plain_value
        assert row[field] is not None


# =============================================================================
# update_connection
# =============================================================================


def test_create_sqlite_connection(sqlite_db):
    """
    Comprueba que se inserta correctamente
    una conexión SQLite en la base de datos.
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
        row = conn.execute(
            "SELECT * FROM connections WHERE id = ?",
            ("1",),
        ).fetchone()

    assert row is not None
    assert row["name"] == "Local"


def test_create_network_connection(sqlite_db):
    """
    Comprueba que se inserta correctamente
    una conexión con driver de red en la
    base de datos.
    """

    conn_obj = Connection(
        id="1",
        name="Remote",
        driver=Driver.POSTGRESQL,
        host="localhost",
        port=5432,
        database="test_db",
        username="postgres",
        password="secret",
    )

    create_connection(conn_obj)

    with sqlite3.connect(sqlite_db) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM connections WHERE id = ?",
            ("1",),
        ).fetchone()

    assert row is not None
    assert row["name"] == "Remote"


@pytest.mark.parametrize(
    ("original_connection", "updated_connection", "encrypted_fields"),
    [
        (
            Connection(
                id="sqlite",
                name="SQLite",
                driver=Driver.SQLITE,
                path="/tmp/old.db",
            ),
            Connection(
                id="sqlite",
                name="Updated SQLite",
                driver=Driver.SQLITE,
                path="/tmp/new.db",
            ),
            {
                "path": "/tmp/new.db",
            },
        ),
        (
            Connection(
                id="postgres",
                name="PostgreSQL",
                driver=Driver.POSTGRESQL,
                host="old-host",
                port=5432,
                database="old_db",
                username="old_user",
                password="old_password",
            ),
            Connection(
                id="postgres",
                name="Updated PostgreSQL",
                driver=Driver.POSTGRESQL,
                host="new-host",
                port=5433,
                database="new_db",
                username="new_user",
                password="new_password",
            ),
            {
                "host": "new-host",
                "port": "5433",
                "database": "new_db",
                "username": "new_user",
                "password": "new_password",
            },
        ),
    ],
)
def test_update_connection_stores_sensitive_data_encrypted(
    sqlite_db,
    original_connection: Connection,
    updated_connection: Connection,
    encrypted_fields: dict[str, str],
):
    """
    Comprueba que, tras actualizar una conexión,
    los datos sensibles permanecen cifrados en la
    base de datos mientras que los campos no
    sensibles se almacenan en texto plano.
    """

    create_connection(original_connection)

    update_connection(updated_connection)

    with sqlite3.connect(sqlite_db) as conn:
        conn.row_factory = sqlite3.Row

        row = conn.execute(
            "SELECT * FROM connections WHERE id = ?",
            (updated_connection.id,),
        ).fetchone()

    assert row is not None

    # Campos no sensibles.
    assert row["id"] == updated_connection.id
    assert row["name"] == updated_connection.name
    assert row["driver"] == updated_connection.driver.value

    # Campos sensibles.
    for field, plain_value in encrypted_fields.items():
        assert row[field] != plain_value
        assert row[field] is not None


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
    Comprueba que se devuelven todas las conexiones
    ordenadas correctamente y con los datos sensibles
    descifrados.
    """

    connections = [
        encrypt(
            Connection(
                id="2",
                name="B",
                driver=Driver.SQLITE,
                path="/tmp/b.db",
            )
        ),
        encrypt(
            Connection(
                id="1",
                name="A",
                driver=Driver.SQLITE,
                path="/tmp/a.db",
            )
        ),
    ]

    with sqlite3.connect(sqlite_db) as conn:
        conn.executemany(
            "INSERT INTO connections VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    c.id,
                    c.name,
                    c.driver.value,
                    c.host,
                    c.port,
                    c.database,
                    c.username,
                    c.password,
                    c.path,
                )
                for c in connections
            ],
        )
        conn.commit()

    result = get_all_connections()

    assert len(result) == 2

    assert result[0].name == "A"
    assert result[0].path == "/tmp/a.db"

    assert result[1].name == "B"
    assert result[1].path == "/tmp/b.db"

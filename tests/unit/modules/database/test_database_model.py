import sqlite3

import pytest

from modules.database.model import (
    get_connection,
    init_database,
)

# =============================================================================
# Fixture local
# =============================================================================


@pytest.fixture
def sqlite_db(tmp_path):
    """
    Crea una base de datos SQLite vacía para tests.
    """
    db_file = tmp_path / "test.db"
    sqlite3.connect(db_file).close()
    return db_file


# =============================================================================
# get_connection
# =============================================================================


def test_get_connection_opens_and_closes_connection(sqlite_db):
    """
    Verifica que el context manager abre correctamente
    una conexión SQLite y la cierra sin errores.
    """

    with get_connection(str(sqlite_db)) as conn:
        assert isinstance(conn, sqlite3.Connection)


def test_get_connection_commits_on_success(sqlite_db):
    """
    Verifica que una transacción exitosa se confirma (commit)
    y los cambios persisten en la base de datos.
    """

    with get_connection(str(sqlite_db)) as conn:
        conn.execute("CREATE TABLE test (id INTEGER)")

    with sqlite3.connect(sqlite_db) as conn:
        cur = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='test'"
        )
        assert cur.fetchone() is not None


def test_get_connection_rolls_back_on_error(sqlite_db):
    """
    Verifica que si ocurre un error dentro del contexto,
    se ejecuta rollback y no se persisten cambios.
    """

    with sqlite3.connect(sqlite_db) as conn:
        conn.execute("CREATE TABLE test (id INTEGER)")
        conn.commit()

    with pytest.raises(sqlite3.Error):
        with get_connection(str(sqlite_db)) as conn:
            conn.execute("INSERT INTO test (id) VALUES (1)")
            raise sqlite3.Error("forced error")

    with sqlite3.connect(sqlite_db) as conn:
        cur = conn.execute("SELECT COUNT(*) FROM test")
        assert cur.fetchone()[0] == 0


# =============================================================================
# init_database
# =============================================================================


def test_init_database_creates_db_and_schema(tmp_path):
    """
    Verifica que init_database:
    - Crea el archivo de base de datos.
    - Ejecuta correctamente el schema SQL.
    """

    db_file = tmp_path / "app.db"
    sql_file = tmp_path / "schema.sql"

    sql_file.write_text(
        """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY
        );
        """,
        encoding="utf-8",
    )

    init_database(
        db_path=str(db_file),
        sql_path=str(sql_file),
        data_dir=str(tmp_path),
    )

    assert db_file.exists()

    with sqlite3.connect(db_file) as conn:
        cur = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
        )
        assert cur.fetchone() is not None


def test_init_database_skips_if_db_exists(tmp_path):
    """
    Verifica que init_database no vuelve a ejecutar
    la inicialización si la base de datos ya existe.
    """

    db_file = tmp_path / "app.db"
    sql_file = tmp_path / "schema.sql"

    sql_file.write_text(
        "CREATE TABLE t (id INTEGER);",
        encoding="utf-8",
    )

    sqlite3.connect(db_file).close()

    init_database(
        db_path=str(db_file),
        sql_path=str(sql_file),
        data_dir=str(tmp_path),
    )

    assert db_file.exists()


def test_init_database_raises_if_sql_missing(tmp_path):
    """
    Verifica que init_database lanza FileNotFoundError
    cuando el archivo SQL no existe.
    """

    db_file = tmp_path / "app.db"
    sql_file = tmp_path / "missing.sql"

    with pytest.raises(FileNotFoundError):
        init_database(
            db_path=str(db_file),
            sql_path=str(sql_file),
            data_dir=str(tmp_path),
        )


def test_init_database_skips_if_db_exists_when_enabled(
    tmp_path,
    monkeypatch,
):
    """
    Si SKIP_INIT_IF_DB_EXISTS está habilitado y la base
    de datos existe, la inicialización debe omitirse.
    """

    from modules.database import model

    db_file = tmp_path / "app.db"
    sqlite3.connect(db_file).close()

    assert db_file.exists()

    monkeypatch.setattr(
        model,
        "SKIP_INIT_IF_DB_EXISTS",
        True,
    )

    # Si no hiciera el return, lanzaría FileNotFoundError.
    model.init_database(
        db_path=str(db_file),
        sql_path="missing.sql",
        data_dir=str(tmp_path),
    )


def test_init_database_does_not_skip_when_db_does_not_exist(
    tmp_path,
    monkeypatch,
):
    """
    Si SKIP_INIT_IF_DB_EXISTS está habilitado pero la base de
    datos no existe, debe continuar con la inicialización.
    """

    import modules.database.model as model

    db_file = tmp_path / "app.db"
    sql_file = tmp_path / "schema.sql"

    sql_file.write_text(
        "CREATE TABLE test (id INTEGER);",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        model,
        "SKIP_INIT_IF_DB_EXISTS",
        True,
    )

    model.init_database(
        db_path=str(db_file),
        sql_path=str(sql_file),
        data_dir=str(tmp_path),
    )

    assert db_file.exists()

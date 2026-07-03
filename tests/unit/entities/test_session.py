from unittest.mock import MagicMock

import pytest

from entities.connection import Connection
from entities.driver import Driver
from entities.session import Session

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def sqlite_connection():
    """
    Devuelve una conexión SQLite de prueba.
    """

    return Connection(
        id="1",
        name="SQLite",
        driver=Driver.SQLITE,
        path="/tmp/test.db",
    )


# =============================================================================
# create
# =============================================================================


def test_create(monkeypatch, sqlite_connection):
    """
    Verifica que create() construye correctamente la sesión.
    """

    fake_engine = MagicMock()

    build_url = MagicMock(return_value="sqlite:///tmp.db")
    build_engine = MagicMock(return_value=fake_engine)

    monkeypatch.setattr(Session, "_build_connection_url", build_url)
    monkeypatch.setattr(Session, "_build_engine", build_engine)

    session = Session.create(sqlite_connection)

    build_url.assert_called_once_with(sqlite_connection)
    build_engine.assert_called_once_with(sqlite_connection, "sqlite:///tmp.db")

    assert session.connection is sqlite_connection
    assert session.engine is fake_engine


# =============================================================================
# _build_connection_url
# =============================================================================


def test_build_connection_url_sqlite(sqlite_connection):
    """
    Verifica la URL SQLite.
    """

    url = Session._build_connection_url(sqlite_connection)

    assert url == "sqlite:////tmp/test.db"


def test_build_connection_url_postgresql():
    """
    Verifica la URL PostgreSQL.
    """

    conn = Connection(
        driver=Driver.POSTGRESQL,
        username="user",
        password="pass",
        host="localhost",
        port=5432,
        database="db",
    )

    url = Session._build_connection_url(conn)

    assert url == "postgresql+psycopg://user:pass@localhost:5432/db"


def test_build_connection_url_mysql():
    """
    Verifica la URL MySQL.
    """

    conn = Connection(
        driver=Driver.MYSQL,
        username="user",
        password="pass",
        host="localhost",
        port=3306,
        database="db",
    )

    url = Session._build_connection_url(conn)

    assert url == "mysql+pymysql://user:pass@localhost:3306/db"


def test_build_connection_url_oracle():
    """
    Verifica la URL Oracle.
    """

    conn = Connection(
        driver=Driver.ORACLE,
        username="user",
        password="pass",
        host="localhost",
        port=1521,
        database="XE",
    )

    url = Session._build_connection_url(conn)

    assert url == "oracle+oracledb://user:pass@localhost:1521/?service_name=XE"


def test_build_connection_url_invalid_driver():
    """
    Verifica que un driver no soportado produce ValueError.
    """

    conn = Connection(driver=MagicMock())

    with pytest.raises(ValueError):
        Session._build_connection_url(conn)


# =============================================================================
# _build_engine
# =============================================================================


@pytest.mark.parametrize(
    "driver,url,kwargs",
    [
        (
            Driver.SQLITE,
            "sqlite:///tmp.db",
            {
                "poolclass": object,
            },
        ),
        (
            Driver.POSTGRESQL,
            "postgres://",
            {
                "pool_pre_ping": True,
                "pool_recycle": 3600,
                "connect_args": {"connect_timeout": 5},
            },
        ),
        (
            Driver.MYSQL,
            "mysql://",
            {
                "pool_pre_ping": True,
                "pool_recycle": 3600,
                "connect_args": {"connect_timeout": 5},
            },
        ),
        (
            Driver.ORACLE,
            "oracle://",
            {
                "pool_pre_ping": True,
                "pool_recycle": 3600,
                "connect_args": {"tcp_connect_timeout": 5},
            },
        ),
    ],
)
def test_build_engine(monkeypatch, driver, url, kwargs):
    """
    Verifica que create_engine se invoca correctamente
    para cada driver soportado.
    """

    fake_engine = MagicMock()

    create_engine = MagicMock(return_value=fake_engine)

    monkeypatch.setattr(
        "entities.session.create_engine",
        create_engine,
    )

    conn = Connection(
        name="Test",
        driver=driver,
    )

    engine = Session._build_engine(conn, url)

    assert engine is fake_engine

    args, call_kwargs = create_engine.call_args

    assert args[0] == url

    if driver == Driver.SQLITE:
        assert "poolclass" in call_kwargs
    else:
        assert call_kwargs["pool_pre_ping"] is True
        assert call_kwargs["pool_recycle"] == 3600


def test_build_engine_invalid_driver():
    """
    Verifica que un driver no soportado produce ValueError.
    """

    conn = Connection(
        name="Test",
        driver=MagicMock(),
    )

    with pytest.raises(ValueError):
        Session._build_engine(conn, "url")


# =============================================================================
# close
# =============================================================================


def test_close():
    """
    Verifica que close() libera el engine.
    """

    engine = MagicMock()

    session = Session(
        connection=Connection(
            name="SQLite",
            driver=Driver.SQLITE,
        ),
        engine=engine,
    )

    session.close()

    engine.dispose.assert_called_once()

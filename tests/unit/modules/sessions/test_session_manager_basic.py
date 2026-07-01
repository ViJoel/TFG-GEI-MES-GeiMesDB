import logging
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import SQLAlchemyError

import modules.sessions.manager as manager
from entities.connection import Connection
from entities.driver import Driver
from entities.session import Session

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture(autouse=True)
def clear_sessions():
    """
    Limpia el registro global de sesiones antes
    y después de cada prueba.
    """

    manager._active_sessions.clear()

    yield

    manager._active_sessions.clear()


@pytest.fixture(autouse=True)
def patch_logger_success(monkeypatch):
    """
    Evita fallos por logger.success.
    """

    logger = logging.getLogger("modules.sessions.manager")
    monkeypatch.setattr(logger, "success", logger.info, raising=False)


def create_connection():
    """
    Construye una conexión SQLite válida para pruebas.
    """

    return Connection(
        id="1",
        name="SQLite",
        driver=Driver.SQLITE,
        path="test.db",
    )


def create_session(connection):
    """
    Construye una sesión simulada.
    """

    session = MagicMock(spec=Session)
    session.connection = connection
    session.engine = MagicMock()

    return session


# =============================================================================
# get_session
# =============================================================================


def test_get_session_existing():
    """
    Debe devolver la sesión registrada.
    """

    connection = create_connection()
    session = create_session(connection)

    manager._active_sessions[connection.id] = session

    assert manager.get_session(connection.id) is session


def test_get_session_not_existing():
    """
    Debe devolver None si no existe.
    """

    assert manager.get_session("missing") is None


# =============================================================================
# has_session
# =============================================================================


def test_has_session_true():
    """
    Debe indicar que existe una sesión.
    """

    connection = create_connection()

    manager._active_sessions[connection.id] = create_session(connection)

    assert manager.has_session(connection.id)


def test_has_session_false():
    """
    Debe indicar que no existe una sesión.
    """

    assert not manager.has_session("missing")


# =============================================================================
# open_session
# =============================================================================


def test_open_session(monkeypatch):
    """
    Debe crear y registrar una sesión activa.
    """

    connection = create_connection()

    session = create_session(connection)

    context = MagicMock()
    context.__enter__.return_value.execute.return_value = None
    session.engine.connect.return_value = context

    create_mock = MagicMock(return_value=session)

    monkeypatch.setattr(Session, "create", create_mock)

    result = manager.open_session(connection)

    assert result is session
    assert manager.has_session(connection.id)

    create_mock.assert_called_once_with(connection)


def test_open_session_duplicate():
    """
    Debe lanzar ValueError si ya existe una sesión.
    """

    connection = create_connection()

    manager._active_sessions[connection.id] = create_session(connection)

    with pytest.raises(ValueError):
        manager.open_session(connection)


def test_open_session_creation_error(monkeypatch):
    """
    Debe propagar la excepción si falla la creación.
    """

    connection = create_connection()

    monkeypatch.setattr(
        Session,
        "create",
        MagicMock(side_effect=RuntimeError("boom")),
    )

    with pytest.raises(RuntimeError):
        manager.open_session(connection)

    assert not manager.has_session(connection.id)


def test_open_session_closes_session_when_verification_fails(monkeypatch):
    """
    Si la verificación de la conexión falla tras crear la
    sesión, los recursos deben liberarse antes de propagar
    la excepción.
    """

    connection = Connection(
        id="1",
        name="Test",
        driver=Driver.SQLITE,
        path="/tmp/test.db",
    )

    fake_conn = MagicMock()
    fake_conn.execute.side_effect = RuntimeError("boom")

    fake_engine = MagicMock()
    fake_engine.connect.return_value.__enter__.return_value = fake_conn

    fake_session = MagicMock()
    fake_session.engine = fake_engine

    monkeypatch.setattr(
        Session,
        "create",
        MagicMock(return_value=fake_session),
    )

    with pytest.raises(RuntimeError):
        manager.open_session(connection)

    fake_session.close.assert_called_once()
    assert connection.id not in manager._active_sessions


def test_open_session_ignores_close_errors(monkeypatch):
    """
    Si la creación de la sesión falla y además
    falla la liberación de recursos, debe
    propagarse únicamente la excepción original.
    """

    connection = Connection(
        id="1",
        name="Test",
        driver=Driver.SQLITE,
        path="/tmp/test.db",
    )

    # La verificación de la conexión falla
    fake_conn = MagicMock()
    fake_conn.execute.side_effect = RuntimeError("verification failed")

    fake_engine = MagicMock()
    fake_engine.connect.return_value.__enter__.return_value = fake_conn

    fake_session = MagicMock()
    fake_session.engine = fake_engine

    # También falla el cierre de la sesión
    fake_session.close.side_effect = RuntimeError("close failed")

    monkeypatch.setattr(
        Session,
        "create",
        MagicMock(return_value=fake_session),
    )

    with pytest.raises(RuntimeError, match="verification failed"):
        manager.open_session(connection)

    fake_session.close.assert_called_once()


# =============================================================================
# close_session
# =============================================================================


def test_close_session():
    """
    Debe cerrar y eliminar la sesión registrada.
    """

    connection = create_connection()

    session = create_session(connection)

    manager._active_sessions[connection.id] = session

    manager.close_session(connection.id)

    session.close.assert_called_once()

    assert not manager.has_session(connection.id)


def test_close_session_not_existing():
    """
    No debe lanzar excepción si no existe.
    """

    manager.close_session("missing")


# =============================================================================
# close_all_sessions
# =============================================================================


def test_close_all_sessions():
    """
    Debe cerrar todas las sesiones activas.
    """

    connection1 = Connection(
        id="1",
        name="A",
        driver=Driver.SQLITE,
        path="a.db",
    )

    connection2 = Connection(
        id="2",
        name="B",
        driver=Driver.SQLITE,
        path="b.db",
    )

    session1 = create_session(connection1)
    session2 = create_session(connection2)

    manager._active_sessions["1"] = session1
    manager._active_sessions["2"] = session2

    manager.close_all_sessions()

    session1.close.assert_called_once()
    session2.close.assert_called_once()

    assert manager._active_sessions == {}


# =============================================================================
# test_connection
# =============================================================================


def test_test_connection_success(monkeypatch):
    """
    Debe devolver True cuando la conexión
    se verifica correctamente.
    """

    connection = Connection(
        id="1",
        name="Test",
        driver=Driver.SQLITE,
        path="/tmp/test.db",
    )

    fake_conn = MagicMock()
    fake_conn.execute.return_value = None

    fake_engine = MagicMock()
    fake_engine.connect.return_value.__enter__.return_value = fake_conn

    fake_session = MagicMock()
    fake_session.engine = fake_engine

    monkeypatch.setattr(
        Session,
        "create",
        MagicMock(return_value=fake_session),
    )

    assert manager.test_connection(connection) is True

    Session.create.assert_called_once_with(connection)
    fake_conn.execute.assert_called_once()
    fake_session.close.assert_called_once()


def test_test_connection_failure(monkeypatch):
    """
    Debe devolver False cuando SQLAlchemy
    lanza una excepción.
    """

    connection = Connection(
        id="1",
        name="Test",
        driver=Driver.SQLITE,
        path="/tmp/test.db",
    )

    fake_conn = MagicMock()
    fake_conn.execute.side_effect = SQLAlchemyError("boom")

    fake_engine = MagicMock()
    fake_engine.connect.return_value.__enter__.return_value = fake_conn

    fake_session = MagicMock()
    fake_session.engine = fake_engine

    monkeypatch.setattr(
        Session,
        "create",
        MagicMock(return_value=fake_session),
    )

    assert manager.test_connection(connection) is False

    fake_session.close.assert_called_once()


def test_test_connection_close_called_if_session_creation_fails(monkeypatch):
    """
    Si la creación de la sesión falla antes
    de devolver una Session, no debe intentar
    cerrar recursos inexistentes.
    """

    connection = Connection(
        id="1",
        name="Test",
        driver=Driver.SQLITE,
        path="/tmp/test.db",
    )

    monkeypatch.setattr(
        Session,
        "create",
        MagicMock(side_effect=SQLAlchemyError("boom")),
    )

    assert manager.test_connection(connection) is False


def test_test_connection_oracle(monkeypatch):
    """
    Oracle debe utilizar la consulta
    SELECT 1 FROM DUAL.
    """

    connection = Connection(
        id="1",
        name="Oracle",
        driver=Driver.ORACLE,
        host="localhost",
        port=1521,
        database="XE",
        username="user",
        password="pwd",
    )

    fake_conn = MagicMock()

    fake_engine = MagicMock()
    fake_engine.connect.return_value.__enter__.return_value = fake_conn

    fake_session = MagicMock()
    fake_session.engine = fake_engine

    monkeypatch.setattr(
        Session,
        "create",
        MagicMock(return_value=fake_session),
    )

    assert manager.test_connection(connection) is True

    executed = fake_conn.execute.call_args.args[0]

    assert str(executed) == "SELECT 1 FROM DUAL"

    fake_session.close.assert_called_once()

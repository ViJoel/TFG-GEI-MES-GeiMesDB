from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import SQLAlchemyError

import modules.sessions.manager as manager
from entities.connection import Connection
from entities.driver import Driver
from entities.query_result import QueryResult, ResultSet
from entities.session import Session

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture(autouse=True)
def clear_sessions():
    """
    Limpia el registro global de sesiones.
    """

    manager._active_sessions.clear()

    yield

    manager._active_sessions.clear()


def create_session():
    """
    Construye una sesión simulada.
    """

    connection = Connection(
        id="1",
        name="SQLite",
        driver=Driver.SQLITE,
        path="test.db",
    )

    session = MagicMock(spec=Session)
    session.connection = connection
    session.engine = MagicMock()

    return session


# =============================================================================
# execute_query
# =============================================================================


def test_execute_query_without_session():
    """
    Debe devolver error si no existe una sesión activa.
    """

    result = manager.execute_query(
        "missing",
        "SELECT * FROM users",
    )

    assert result.success is False
    assert result.result_set is None
    assert "There is no active session" in result.console_output


def test_execute_query_select(monkeypatch):
    """
    Debe construir un QueryResult cuando la consulta devuelve filas.
    """

    session = create_session()

    manager._active_sessions["1"] = session

    result = MagicMock()
    result.returns_rows = True

    context = MagicMock()
    context.__enter__.return_value.execute.return_value = result

    session.engine.begin.return_value = context

    expected = QueryResult(
        success=True,
        console_output="OK",
        result_set=MagicMock(),
    )

    monkeypatch.setattr(
        manager,
        "_create_query_result",
        MagicMock(return_value=expected),
    )

    qr = manager.execute_query(
        "1",
        "SELECT * FROM users",
    )

    assert qr is expected


def test_execute_query_update():
    """
    Debe generar salida de consola para consultas sin filas.
    """

    session = create_session()

    manager._active_sessions["1"] = session

    result = MagicMock()
    result.returns_rows = False
    result.rowcount = 2

    context = MagicMock()
    context.__enter__.return_value.execute.return_value = result

    session.engine.begin.return_value = context

    qr = manager.execute_query(
        "1",
        "UPDATE users SET name='A'",
    )

    assert qr.success
    assert qr.result_set is None
    assert qr.console_output == "2 row(s) updated."


def test_execute_query_sqlalchemy_error():
    """
    Debe devolver un QueryResult fallido cuando SQLAlchemy lanza una excepción.
    """

    session = create_session()

    manager._active_sessions["1"] = session

    context = MagicMock()
    context.__enter__.return_value.execute.side_effect = SQLAlchemyError("boom")

    session.engine.begin.return_value = context

    qr = manager.execute_query(
        "1",
        "SELECT * FROM users",
    )

    assert not qr.success
    assert "boom" in qr.console_output


def test_execute_query_unexpected_error():
    """
    Debe capturar errores inesperados.
    """

    session = create_session()

    manager._active_sessions["1"] = session

    context = MagicMock()
    context.__enter__.return_value.execute.side_effect = RuntimeError()

    session.engine.begin.return_value = context

    qr = manager.execute_query(
        "1",
        "SELECT * FROM users",
    )

    assert not qr.success
    assert "Unexpected internal error" in qr.console_output


# =============================================================================
# _create_result_set
# =============================================================================


def test_create_result_set(monkeypatch):
    """
    Debe construir correctamente un ResultSet.
    """

    result = MagicMock()

    result.keys.return_value = ["id", "name"]
    result.fetchall.return_value = [
        (1, "Alice"),
        (2, "Bob"),
    ]

    monkeypatch.setattr(
        manager,
        "_get_editable_metadata",
        MagicMock(return_value=("users", ["id"])),
    )

    rs = manager._create_result_set(
        engine=MagicMock(),
        query="SELECT * FROM users",
        result=result,
    )

    assert isinstance(rs, ResultSet)
    assert rs.columns == ["id", "name"]
    assert rs.rows == [[1, "Alice"], [2, "Bob"]]
    assert rs.table_name == "users"
    assert rs.primary_key_columns == ["id"]


# =============================================================================
# _create_query_result
# =============================================================================


def test_create_query_result(monkeypatch):
    """
    Debe construir correctamente un QueryResult.
    """

    rs = ResultSet(
        rows=[[1]],
        columns=["id"],
        columns_types=[int],
        table_name="users",
        primary_key_columns=["id"],
    )

    monkeypatch.setattr(
        manager,
        "_create_result_set",
        MagicMock(return_value=rs),
    )

    qr = manager._create_query_result(
        engine=MagicMock(),
        query="SELECT * FROM users",
        result=MagicMock(),
    )

    assert qr.success
    assert qr.result_set is rs
    assert "1 row(s) returned." in qr.console_output

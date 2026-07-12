from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import SQLAlchemyError

import modules.sessions.manager as manager
from entities.connection import Connection
from entities.driver import Driver
from entities.query_result import (
    QueryResult,
    ResultSet,
)
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


def test_open_session_oracle(monkeypatch):
    """
    Oracle debe utilizar la consulta
    SELECT 1 FROM DUAL al verificar
    la conexión.
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
    fake_session.connection = connection

    monkeypatch.setattr(
        Session,
        "create",
        MagicMock(return_value=fake_session),
    )

    returned = manager.open_session(connection)

    assert returned is fake_session
    assert manager.has_session(connection.id)

    executed = fake_conn.execute.call_args.args[0]

    assert str(executed) == "SELECT 1 FROM DUAL"


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


def test_close_session_close_error():
    """
    Debe propagar la excepción si falla el
    cierre de la sesión.
    """

    connection = create_connection()

    session = create_session(connection)
    session.close.side_effect = RuntimeError("boom")

    manager._active_sessions[connection.id] = session

    with pytest.raises(RuntimeError, match="boom"):
        manager.close_session(connection.id)

    session.close.assert_called_once()

    # La sesión sigue registrada porque el cierre falló
    assert manager.has_session(connection.id)


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


# =============================================================================
# execute_query
# =============================================================================


def test_execute_query_without_session():
    """
    Debe devolver un error cuando no existe
    una sesión activa.
    """

    result = manager.execute_query(
        connection_id="missing",
        query="SELECT 1",
    )

    assert result.success is False
    assert result.result_set is None
    assert "There is no active session" in result.console_output


def test_execute_query_select(monkeypatch):
    """
    Debe devolver un QueryResult con ResultSet
    cuando la consulta devuelve filas.
    """

    connection = create_connection()
    session = create_session(connection)

    result = MagicMock()
    result.returns_rows = True

    conn = MagicMock()
    conn.execute.return_value = result

    session.engine.begin.return_value.__enter__.return_value = conn

    manager._active_sessions[connection.id] = session

    expected = MagicMock()

    create_query_result = MagicMock(return_value=expected)

    monkeypatch.setattr(
        manager,
        "_create_query_result",
        create_query_result,
    )

    query = "SELECT * FROM users"

    returned = manager.execute_query(
        connection.id,
        query,
    )

    assert returned is expected

    create_query_result.assert_called_once_with(
        engine=session.engine,
        query=query,
        result=result,
    )


def test_execute_query_insert():
    """
    INSERT debe generar el mensaje correcto.
    """

    connection = create_connection()
    session = create_session(connection)

    result = MagicMock()
    result.returns_rows = False
    result.rowcount = 3

    conn = MagicMock()
    conn.execute.return_value = result

    session.engine.begin.return_value.__enter__.return_value = conn

    manager._active_sessions[connection.id] = session

    returned = manager.execute_query(
        connection.id,
        "INSERT INTO users VALUES (1)",
    )

    assert returned.success
    assert returned.result_set is None
    assert returned.console_output == "3 row(s) inserted."


def test_execute_query_update():
    """
    UPDATE debe generar el mensaje correcto.
    """

    connection = create_connection()
    session = create_session(connection)

    result = MagicMock()
    result.returns_rows = False
    result.rowcount = 5

    conn = MagicMock()
    conn.execute.return_value = result

    session.engine.begin.return_value.__enter__.return_value = conn

    manager._active_sessions[connection.id] = session

    returned = manager.execute_query(
        connection.id,
        "UPDATE users SET name='A'",
    )

    assert returned.success
    assert returned.console_output == "5 row(s) updated."


def test_execute_query_delete():
    """
    DELETE debe generar el mensaje correcto.
    """

    connection = create_connection()
    session = create_session(connection)

    result = MagicMock()
    result.returns_rows = False
    result.rowcount = 2

    conn = MagicMock()
    conn.execute.return_value = result

    session.engine.begin.return_value.__enter__.return_value = conn

    manager._active_sessions[connection.id] = session

    returned = manager.execute_query(
        connection.id,
        "DELETE FROM users",
    )

    assert returned.success
    assert returned.console_output == "2 row(s) deleted."


def test_execute_query_other_command():
    """
    Consultas que no son INSERT/UPDATE/DELETE
    deben devolver el mensaje genérico.
    """

    connection = create_connection()
    session = create_session(connection)

    result = MagicMock()
    result.returns_rows = False
    result.rowcount = 0

    conn = MagicMock()
    conn.execute.return_value = result

    session.engine.begin.return_value.__enter__.return_value = conn

    manager._active_sessions[connection.id] = session

    returned = manager.execute_query(
        connection.id,
        "CREATE TABLE users(id INTEGER)",
    )

    assert returned.success
    assert returned.console_output == "Query executed successfully."


def test_execute_query_sqlalchemy_error():
    """
    Debe devolver success=False cuando
    SQLAlchemy lanza una excepción.
    """

    connection = create_connection()
    session = create_session(connection)

    conn = MagicMock()
    conn.execute.side_effect = SQLAlchemyError("boom")

    session.engine.begin.return_value.__enter__.return_value = conn

    manager._active_sessions[connection.id] = session

    returned = manager.execute_query(
        connection.id,
        "SELECT 1",
    )

    assert not returned.success
    assert returned.result_set is None
    assert returned.console_output == "boom"


def test_execute_query_unexpected_exception():
    """
    Debe capturar excepciones inesperadas.
    """

    connection = create_connection()
    session = create_session(connection)

    conn = MagicMock()
    conn.execute.side_effect = RuntimeError("boom")

    session.engine.begin.return_value.__enter__.return_value = conn

    manager._active_sessions[connection.id] = session

    returned = manager.execute_query(
        connection.id,
        "SELECT 1",
    )

    assert returned.success is False
    assert returned.result_set is None
    assert returned.console_output == (
        "Unexpected internal error.\nSee logs for details."
    )


# =============================================================================
# execute_script
# =============================================================================


def test_execute_script_all_success(monkeypatch):
    """
    Debe crear un ScriptResult sin errores cuando
    todas las consultas se ejecutan correctamente.
    """

    monkeypatch.setattr(
        manager,
        "execute_query",
        MagicMock(
            return_value=QueryResult(
                success=True,
                console_output="ok",
                result_set=None,
            )
        ),
    )

    result = manager.execute_script(
        connection_id="1",
        queries=[
            "SELECT 1",
            "SELECT 2",
        ],
    )

    assert len(result.items) == 2

    assert result.items[0].query == "SELECT 1"
    assert result.items[0].error is None

    assert result.items[1].query == "SELECT 2"
    assert result.items[1].error is None


def test_execute_script_with_errors(monkeypatch):
    """
    Debe almacenar el mensaje de error cuando
    una consulta falla.
    """

    execute = MagicMock(
        side_effect=[
            QueryResult(
                success=True,
                console_output="",
                result_set=None,
            ),
            QueryResult(
                success=False,
                console_output="boom",
                result_set=None,
            ),
        ]
    )

    monkeypatch.setattr(
        manager,
        "execute_query",
        execute,
    )

    result = manager.execute_script(
        connection_id="1",
        queries=[
            "SELECT 1",
            "SELECT 2",
        ],
    )

    assert len(result.items) == 2

    assert result.items[0].error is None
    assert result.items[1].error == "boom"


# =============================================================================
# is_editable_query
# =============================================================================


def test_is_editable_query_valid():

    assert manager.is_editable_query("SELECT * FROM users")


def test_is_editable_query_valid_with_spaces():

    assert manager.is_editable_query("""
            SELECT
                *
            FROM
                users
        """)


@pytest.mark.parametrize(
    "query",
    [
        "SELECT id FROM users",
        "SELECT DISTINCT * FROM users",
        "SELECT * FROM users WHERE id=1",
        "SELECT * FROM users JOIN roles",
        "SELECT * FROM users GROUP BY id",
        "SELECT * FROM users HAVING COUNT(*)>1",
        "SELECT * FROM users LIMIT 10",
        "SELECT * FROM users UNION SELECT * FROM other",
        "SELECT * FROM users INTERSECT SELECT * FROM other",
        "SELECT * FROM users EXCEPT SELECT * FROM other",
        "WITH cte AS (SELECT * FROM users) SELECT * FROM cte",
        "SELECT * FROM users OFFSET 10",
        "SELECT * INTO backup FROM users",
    ],
)
def test_is_editable_query_invalid(query):

    assert not manager.is_editable_query(query)


# =============================================================================
# _infer_column_types
# =============================================================================


def test_infer_column_types():

    result = manager._infer_column_types(
        columns=["id", "name", "active"],
        rows=[
            [1, "Ana", True],
            [2, "Luis", False],
        ],
    )

    assert result == [int, str, bool]


def test_infer_column_types_first_row_none():

    result = manager._infer_column_types(
        columns=["id"],
        rows=[
            [None],
            [5],
        ],
    )

    assert result == [int]


def test_infer_column_types_all_none():

    result = manager._infer_column_types(
        columns=["id"],
        rows=[
            [None],
            [None],
        ],
    )

    assert result == [str]


# =============================================================================
# _extract_table_name
# =============================================================================


def test_extract_table_name():

    assert manager._extract_table_name("SELECT * FROM users") == "users"


def test_extract_table_name_semicolon():

    assert manager._extract_table_name("SELECT * FROM users;") == "users"


def test_extract_table_name_invalid():

    assert manager._extract_table_name("SELECT") is None


# =============================================================================
# _create_console_output
# =============================================================================


@pytest.mark.parametrize(
    ("query", "rowcount", "expected"),
    [
        ("INSERT INTO users VALUES(1)", 1, "1 row(s) inserted."),
        ("UPDATE users SET name='A'", 2, "2 row(s) updated."),
        ("DELETE FROM users", 3, "3 row(s) deleted."),
        ("CREATE TABLE users(id)", 0, "Query executed successfully."),
    ],
)
def test_create_console_output(query, rowcount, expected):

    result = MagicMock()
    result.rowcount = rowcount

    assert (
        manager._create_console_output(
            query=query,
            result=result,
        )
        == expected
    )


# =============================================================================
# _format_result_set
# =============================================================================


def test_format_result_set():

    result_set = ResultSet(
        rows=[
            [1, "Ana"],
            [20, "Luis"],
        ],
        columns=["id", "name"],
        columns_types=[int, str],
        table_name=None,
        primary_key_columns=[],
    )

    text = manager._format_result_set(result_set)

    assert "id" in text
    assert "name" in text
    assert "Ana" in text
    assert "Luis" in text
    assert "|" in text
    assert "-+-" in text


# =============================================================================
# _get_primary_key_columns
# =============================================================================


def test_get_primary_key_columns(monkeypatch):

    inspector = MagicMock()
    inspector.get_pk_constraint.return_value = {
        "constrained_columns": ["id"],
    }

    monkeypatch.setattr(
        manager,
        "inspect",
        MagicMock(return_value=inspector),
    )

    assert manager._get_primary_key_columns(
        engine=MagicMock(),
        table_name="users",
    ) == ["id"]

    inspector.get_pk_constraint.assert_called_once_with("users")


def test_get_primary_key_columns_without_pk(monkeypatch):

    inspector = MagicMock()
    inspector.get_pk_constraint.return_value = {}

    monkeypatch.setattr(
        manager,
        "inspect",
        MagicMock(return_value=inspector),
    )

    assert (
        manager._get_primary_key_columns(
            engine=MagicMock(),
            table_name="users",
        )
        == []
    )


# =============================================================================
# _get_editable_metadata
# =============================================================================


def test_get_editable_metadata_not_editable(monkeypatch):

    monkeypatch.setattr(
        manager,
        "is_editable_query",
        MagicMock(return_value=False),
    )

    table, pk = manager._get_editable_metadata(
        query="SELECT id FROM users",
        engine=MagicMock(),
    )

    assert table is None
    assert pk == []


def test_get_editable_metadata_without_table(monkeypatch):

    monkeypatch.setattr(
        manager,
        "is_editable_query",
        MagicMock(return_value=True),
    )

    monkeypatch.setattr(
        manager,
        "_extract_table_name",
        MagicMock(return_value=None),
    )

    table, pk = manager._get_editable_metadata(
        query="SELECT * FROM users",
        engine=MagicMock(),
    )

    assert table is None
    assert pk == []


def test_get_editable_metadata(monkeypatch):

    monkeypatch.setattr(
        manager,
        "is_editable_query",
        MagicMock(return_value=True),
    )

    monkeypatch.setattr(
        manager,
        "_extract_table_name",
        MagicMock(return_value="users"),
    )

    monkeypatch.setattr(
        manager,
        "_get_primary_key_columns",
        MagicMock(return_value=["id"]),
    )

    table, pk = manager._get_editable_metadata(
        query="SELECT * FROM users",
        engine=MagicMock(),
    )

    assert table == "users"
    assert pk == ["id"]


# =============================================================================
# _create_result_set
# =============================================================================


def test_create_result_set(monkeypatch):

    result = MagicMock()

    result.keys.return_value = ["id", "name"]

    result.fetchall.return_value = [
        (1, "Ana"),
        (2, "Luis"),
    ]

    monkeypatch.setattr(
        manager,
        "_get_editable_metadata",
        MagicMock(
            return_value=(
                "users",
                ["id"],
            )
        ),
    )

    result_set = manager._create_result_set(
        engine=MagicMock(),
        query="SELECT * FROM users",
        result=result,
    )

    assert result_set.columns == ["id", "name"]
    assert result_set.rows == [
        [1, "Ana"],
        [2, "Luis"],
    ]
    assert result_set.columns_types == [int, str]
    assert result_set.table_name == "users"
    assert result_set.primary_key_columns == ["id"]


# =============================================================================
# _create_query_result
# =============================================================================


def test_create_query_result(monkeypatch):

    result_set = ResultSet(
        rows=[
            [1, "Ana"],
            [2, "Luis"],
        ],
        columns=["id", "name"],
        columns_types=[int, str],
        table_name="users",
        primary_key_columns=["id"],
    )

    monkeypatch.setattr(
        manager,
        "_create_result_set",
        MagicMock(return_value=result_set),
    )

    result = manager._create_query_result(
        engine=MagicMock(),
        query="SELECT * FROM users",
        result=MagicMock(),
    )

    assert result.success
    assert result.result_set is result_set
    assert "2 row(s) returned." in result.console_output
    assert "Ana" in result.console_output
    assert "Luis" in result.console_output

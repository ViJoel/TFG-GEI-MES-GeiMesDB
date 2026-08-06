from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import SQLAlchemyError

import modules.sessions.manager as manager
from entities.connection import Connection
from entities.driver import Driver
from entities.query_result import QueryResult
from entities.session import Session
from entities.update_operation import UpdateOperation

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
# execute_updates
# =============================================================================


def test_execute_updates_without_session():
    """
    Debe devolver un ScriptResult con error cuando
    no existe una sesión activa.
    """

    result = manager.execute_updates(
        connection_id="missing",
        operations=[],
    )

    assert result.rolled_back is False
    assert len(result.items) == 1
    assert result.items[0].error is not None
    assert "There is no active session" in result.items[0].error


def test_execute_updates_all_success():
    """
    Debe ejecutar todas las operaciones y hacer
    commit de la transacción.
    """

    connection = create_connection()
    session = create_session(connection)

    manager._active_sessions[connection.id] = session

    conn = MagicMock()

    transaction = MagicMock()
    savepoint = MagicMock()

    conn.begin.return_value = transaction
    conn.begin_nested.return_value = savepoint

    session.engine.connect.return_value.__enter__.return_value = conn
    session.engine.dialect = MagicMock()

    op1 = MagicMock(spec=UpdateOperation)
    op1.to_statement.return_value = "stmt1"
    op1.to_sql.return_value = "sql1"

    op2 = MagicMock(spec=UpdateOperation)
    op2.to_statement.return_value = "stmt2"
    op2.to_sql.return_value = "sql2"

    result = manager.execute_updates(
        connection.id,
        [op1, op2],
    )

    assert result.rolled_back is False
    assert len(result.items) == 2

    transaction.commit.assert_called_once()
    transaction.rollback.assert_not_called()

    assert savepoint.commit.call_count == 2
    savepoint.rollback.assert_not_called()

    assert result.items[0].query == "sql1"
    assert result.items[0].error is None

    assert result.items[1].query == "sql2"
    assert result.items[1].error is None


def test_execute_updates_with_sqlalchemy_error():
    """
    Si una operación falla debe hacerse rollback
    completo al finalizar.
    """

    connection = create_connection()
    session = create_session(connection)

    manager._active_sessions[connection.id] = session

    conn = MagicMock()

    transaction = MagicMock()

    savepoint_ok = MagicMock()
    savepoint_fail = MagicMock()

    conn.begin.return_value = transaction
    conn.begin_nested.side_effect = [
        savepoint_ok,
        savepoint_fail,
    ]

    conn.execute.side_effect = [
        None,
        SQLAlchemyError("boom"),
    ]

    session.engine.connect.return_value.__enter__.return_value = conn
    session.engine.dialect = MagicMock()

    op1 = MagicMock(spec=UpdateOperation)
    op1.to_statement.return_value = "stmt1"
    op1.to_sql.return_value = "sql1"

    op2 = MagicMock(spec=UpdateOperation)
    op2.to_statement.return_value = "stmt2"
    op2.to_sql.return_value = "sql2"

    result = manager.execute_updates(
        connection.id,
        [op1, op2],
    )

    assert result.rolled_back is True

    transaction.rollback.assert_called_once()
    transaction.commit.assert_not_called()

    savepoint_ok.commit.assert_called_once()
    savepoint_fail.rollback.assert_called_once()

    assert result.items[0].error is None
    assert result.items[1].error == "boom"


def test_execute_updates_unexpected_exception():
    """
    Una excepción inesperada al iniciar la
    transacción debe hacer rollback y
    propagarse.
    """

    connection = create_connection()
    session = create_session(connection)

    manager._active_sessions[connection.id] = session

    conn = MagicMock()

    # Error inesperado antes de comenzar la transacción.
    conn.begin.side_effect = RuntimeError("boom")

    session.engine.connect.return_value.__enter__.return_value = conn

    operation = MagicMock(spec=UpdateOperation)

    with pytest.raises(RuntimeError, match="boom"):
        manager.execute_updates(
            connection.id,
            [operation],
        )


def test_execute_updates_prepare_error():
    """
    Si una operación falla durante la preparación
    debe registrarse el error y continuar con el
    resto de operaciones.
    """

    connection = create_connection()
    session = create_session(connection)

    manager._active_sessions[connection.id] = session

    conn = MagicMock()

    transaction = MagicMock()
    savepoint = MagicMock()

    conn.begin.return_value = transaction
    conn.begin_nested.return_value = savepoint

    session.engine.connect.return_value.__enter__.return_value = conn
    session.engine.dialect = MagicMock()

    op1 = MagicMock(spec=UpdateOperation)
    op1.to_statement.side_effect = RuntimeError("boom")

    op2 = MagicMock(spec=UpdateOperation)
    op2.to_statement.return_value = "stmt2"
    op2.to_sql.return_value = "sql2"

    result = manager.execute_updates(
        connection.id,
        [op1, op2],
    )

    assert result.rolled_back is True

    transaction.rollback.assert_called_once()
    transaction.commit.assert_not_called()

    savepoint.commit.assert_called_once()

    assert result.items[0].query == "<Unable to generate SQL>"
    assert result.items[0].error == "boom"

    assert result.items[1].query == "sql2"
    assert result.items[1].error is None

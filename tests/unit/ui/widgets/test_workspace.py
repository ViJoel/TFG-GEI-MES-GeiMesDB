from unittest.mock import MagicMock

import pytest
from PySide6.QtWidgets import QWidget

from entities.connection import Connection
from entities.message_type import MessageType
from entities.navigation_tree_action import NavigationTreeAction
from entities.queries_history_entry import QueriesHistoryEntry
from entities.sql_scope import SqlScope
from entities.unsaved_changes_count import UnsavedChangesCount
from ui.app.worker_error import WorkerError
from ui.widgets.workspace.workspace import Workspace

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture(autouse=True)
def patch_global_dependencies(mocker):
    """
    Bloquea dependencias globales ajenas al componente.
    """

    mocker.patch(
        "ui.widgets.workspace.workspace.notify",
    )

    mocker.patch(
        "ui.widgets.workspace.results_view.results_view.notify",
    )

    mocker.patch(
        "ui.widgets.workspace.results_view.results_view.ConfirmationDialog",
    )

    mocker.patch(
        "ui.widgets.workspace.results_view.connection_queries_history.notify",
    )

    mocker.patch(
        "ui.widgets.workspace.results_view.connection_queries_history.get_queries_history",
        return_value=[],
    )

    mocker.patch(
        "ui.widgets.workspace.results_view.connection_queries_history.AppContext.get_task_manager",
    )

    mocker.patch(
        "ui.widgets.workspace.results_view.connection_queries_history.AppContext.get_app",
    )

    mocker.patch(
        "ui.widgets.workspace.navigation_tree.navigation_tree.notify",
    )

    mocker.patch(
        "ui.widgets.workspace.navigation_tree.navigation_tree.AppContext.get_task_manager",
        return_value=mocker.Mock(),
    )


@pytest.fixture(autouse=True)
def patch_navigation_tree(mocker):

    tree = QWidget()

    tree.refresh = mocker.Mock()
    tree.action_requested = mocker.Mock()
    tree.tree_reloaded = mocker.Mock()

    mocker.patch(
        "ui.widgets.workspace.workspace.NavigationTree",
        return_value=tree,
    )

    return tree


@pytest.fixture
def task_manager(mocker):
    """
    Mock del TaskManager global.
    """

    manager = mocker.Mock()

    mocker.patch(
        "ui.widgets.workspace.workspace.AppContext.get_task_manager",
        return_value=manager,
    )

    return manager


@pytest.fixture
def notify_mock(mocker):
    """
    Mock de la función notify.
    """

    return mocker.patch(
        "ui.widgets.workspace.workspace.notify",
    )


@pytest.fixture
def execute_query_mock(mocker):
    """
    Mock de execute_query().
    """

    return mocker.patch(
        "ui.widgets.workspace.workspace.execute_query",
    )


@pytest.fixture
def execute_script_mock(mocker):
    """
    Mock de execute_script().
    """

    return mocker.patch(
        "ui.widgets.workspace.workspace.execute_script",
    )


@pytest.fixture
def execute_updates_mock(mocker):
    """
    Mock de execute_updates().
    """

    return mocker.patch(
        "ui.widgets.workspace.workspace.execute_updates",
    )


@pytest.fixture
def save_history_mock(mocker):
    """
    Mock de save_queries_history_batch().
    """

    return mocker.patch(
        "ui.widgets.workspace.workspace.save_queries_history_batch",
    )


@pytest.fixture
def editable_query_mock(mocker):
    """
    Mock de is_editable_query().
    """

    return mocker.patch(
        "ui.widgets.workspace.workspace.is_editable_query",
    )


@pytest.fixture
def connection():
    """
    Conexión simulada.
    """

    connection = MagicMock(spec=Connection)

    connection.id = 1
    connection.name = "Test Connection"

    return connection


@pytest.fixture
def workspace(
    qtbot,
    connection,
):
    """
    Workspace registrado en qtbot.
    """

    widget = Workspace(connection)

    qtbot.addWidget(widget)

    return widget


@pytest.fixture
def app_mock(mocker):
    app = mocker.Mock()
    mocker.patch(
        "ui.widgets.workspace.workspace.AppContext.get_app",
        return_value=app,
    )
    return app


# =============================================================================
# ON EXECUTE REQUESTED
# =============================================================================


@pytest.mark.parametrize(
    (
        "scope",
        "queries",
        "execute_query_calls",
        "execute_script_calls",
    ),
    [
        (
            SqlScope.SELECTED_TEXT,
            ["SELECT * FROM users"],
            1,
            0,
        ),
        (
            SqlScope.SELECTED_TEXT,
            [
                "CREATE TABLE test(id INTEGER);",
                "SELECT * FROM test;",
            ],
            0,
            1,
        ),
        (
            SqlScope.ACTUAL_QUERY,
            ["SELECT * FROM users"],
            1,
            0,
        ),
        (
            SqlScope.FULL_SCRIPT,
            [
                "CREATE TABLE test(id INTEGER);",
                "SELECT * FROM test;",
            ],
            0,
            1,
        ),
    ],
)
def test_on_execute_requested_dispatches_execution(
    workspace,
    notify_mock,
    mocker,
    scope,
    queries,
    execute_query_calls,
    execute_script_calls,
):
    """
    Verifica que cada ámbito de ejecución delega
    en el método correspondiente.
    """

    execute_query = mocker.patch.object(
        workspace,
        "_execute_query",
    )

    execute_script = mocker.patch.object(
        workspace,
        "_execute_script",
    )

    save_history = mocker.patch.object(
        workspace,
        "_save_queries_history",
    )

    set_buttons = mocker.patch.object(
        workspace.results_view,
        "set_action_buttons_state",
    )

    workspace._on_execute_requested(
        queries,
        scope,
    )

    assert execute_query.call_count == execute_query_calls
    assert execute_script.call_count == execute_script_calls

    if execute_query_calls:
        execute_query.assert_called_once_with(queries)

    if execute_script_calls:
        execute_script.assert_called_once_with(queries)

    save_history.assert_called_once_with(queries)

    set_buttons.assert_called_once_with(False)

    notify_mock.assert_called_once_with(
        MessageType.WARNING,
        "Executing sql...",
    )


# =============================================================================
# EXECUTE QUERY
# =============================================================================


def test_execute_query_submits_task(
    workspace,
    task_manager,
):
    """
    Verifica que una consulta válida se delega al
    TaskManager para su ejecución en segundo plano.
    """

    query = "SELECT * FROM users"

    workspace._execute_query([query])

    task_manager.run.assert_called_once_with(
        workspace._execute_query_backend,
        query,
        on_success=workspace._on_query_finished,
        on_error=workspace._on_execution_error,
    )


def test_execute_query_aborts_when_multiple_queries_are_received(
    workspace,
    notify_mock,
    task_manager,
    mocker,
):
    """
    Verifica que la ejecución se cancela cuando se
    reciben varias sentencias SQL.
    """

    write_message = mocker.patch.object(
        workspace.results_view,
        "write_message",
    )

    show_console = mocker.patch.object(
        workspace.results_view,
        "show_console",
    )

    workspace._execute_query(
        [
            "SELECT * FROM users;",
            "SELECT * FROM products;",
        ]
    )

    task_manager.run.assert_not_called()

    write_message.assert_called_once()

    show_console.assert_called_once()

    notify_mock.assert_called_once_with(
        MessageType.WARNING,
        "Execution aborted.",
    )


def test_execute_query_backend(
    workspace,
    execute_query_mock,
):
    """
    Verifica que el backend ejecuta la consulta y
    devuelve una entidad QueryExecution.
    """

    result = object()

    execute_query_mock.return_value = result

    query = "SELECT * FROM users"

    execution = workspace._execute_query_backend(query)

    execute_query_mock.assert_called_once_with(
        connection_id=workspace.connection.id,
        query=query,
    )

    assert execution.query == query
    assert execution.result is result


def test_on_query_finished_updates_results_view(
    workspace,
    editable_query_mock,
    mocker,
):
    """
    Verifica que la finalización de una consulta
    actualiza correctamente la interfaz.
    """

    editable_query_mock.return_value = True

    show_result = mocker.patch.object(
        workspace.results_view,
        "show_result",
    )

    set_editable = mocker.patch.object(
        workspace.results_view,
        "set_editable",
    )

    result = object()

    from entities.query_execution import QueryExecution

    execution = QueryExecution(
        query="SELECT * FROM users",
        result=result,
    )

    workspace._on_query_finished(execution)

    assert workspace.current_query == execution.query

    show_result.assert_called_once_with(
        result=result,
        script_result=None,
        is_script=False,
    )

    editable_query_mock.assert_called_once_with(
        execution.query,
    )

    set_editable.assert_called_once_with(True)


def test_on_execution_error(
    workspace,
    notify_mock,
    mocker,
):
    """
    Verifica que un error producido por el worker
    se notifica correctamente.
    """

    logger = mocker.patch(
        "ui.widgets.workspace.workspace.logger",
    )

    from ui.app.worker_error import WorkerError

    error = WorkerError(
        exception=RuntimeError("Boom"),
        traceback="Traceback...",
    )

    workspace._on_execution_error(error)

    logger.error.assert_called_once()

    notify_mock.assert_called_once_with(
        message_type=MessageType.ERROR,
        message="Error in execution.",
    )


# =============================================================================
# EXECUTE SCRIPT
# =============================================================================


def test_execute_script_submits_task(
    workspace,
    task_manager,
):
    """
    Verifica que un script SQL se delega al
    TaskManager para su ejecución en segundo plano.
    """

    queries = [
        "CREATE TABLE test(id INTEGER);",
        "INSERT INTO test VALUES (1);",
    ]

    workspace._execute_script(queries)

    task_manager.run.assert_called_once_with(
        workspace._execute_script_backend,
        queries,
        on_success=workspace._on_script_finished,
        on_error=workspace._on_execution_error,
    )


def test_execute_script_backend(
    workspace,
    execute_script_mock,
):
    """
    Verifica que el backend ejecuta el script y
    devuelve el resultado obtenido.
    """

    script_result = object()

    execute_script_mock.return_value = script_result

    queries = [
        "CREATE TABLE test(id INTEGER);",
        "INSERT INTO test VALUES (1);",
    ]

    result = workspace._execute_script_backend(queries)

    execute_script_mock.assert_called_once_with(
        connection_id=workspace.connection.id,
        queries=queries,
    )

    assert result is script_result


def test_on_script_finished_updates_results_view(
    workspace,
    mocker,
):
    """
    Verifica que la finalización de un script
    actualiza correctamente la interfaz.
    """

    show_result = mocker.patch.object(
        workspace.results_view,
        "show_result",
    )

    set_editable = mocker.patch.object(
        workspace.results_view,
        "set_editable",
    )

    script_result = object()

    workspace._on_script_finished(script_result)

    show_result.assert_called_once_with(
        result=None,
        script_result=script_result,
        is_script=True,
    )

    set_editable.assert_called_once_with(False)


# =============================================================================
# SAVE QUERIES HISTORY
# =============================================================================


def test_save_queries_history_submits_task(
    workspace,
    task_manager,
    mocker,
):
    """
    Verifica que el guardado del historial se
    delega al TaskManager.
    """

    add_entry = mocker.patch.object(
        workspace.results_view,
        "add_entry_to_session_queries_history",
    )

    queries = [
        "SELECT 1",
        "SELECT 2",
    ]

    workspace._save_queries_history(queries)

    assert add_entry.call_count == 2

    task_manager.run.assert_called_once()

    args, kwargs = task_manager.run.call_args

    assert args[0] == workspace._save_queries_history_backend

    entries = args[1]

    assert len(entries) == 2
    assert entries[0].query == "SELECT 1"
    assert entries[1].query == "SELECT 2"

    assert kwargs["on_success"] == workspace._on_save_queries_history_success
    assert kwargs["on_error"] == workspace._on_save_queries_history_error


def test_save_queries_history_backend(
    workspace,
    save_history_mock,
):
    """
    Verifica que el backend persiste el historial
    recibido.
    """

    entries = [
        QueriesHistoryEntry(
            connection_id=1,
            query="SELECT 1",
        ),
        QueriesHistoryEntry(
            connection_id=1,
            query="SELECT 2",
        ),
    ]

    workspace._save_queries_history_backend(entries)

    save_history_mock.assert_called_once_with(
        connection=workspace.connection,
        entries=entries,
    )


def test_on_save_queries_history_success(
    notify_mock,
    workspace,
):
    """
    Verifica que el usuario es notificado cuando
    el historial se guarda correctamente.
    """

    workspace._on_save_queries_history_success(None)

    notify_mock.assert_called_once_with(
        MessageType.SUCCESS,
        "Queries history updated.",
    )


def test_on_save_queries_history_error(
    notify_mock,
    workspace,
):
    """
    Verifica que el usuario es notificado cuando
    falla el guardado del historial.
    """

    error = WorkerError(
        exception=Exception("boom"),
        traceback="traceback",
    )

    workspace._on_save_queries_history_error(error)

    notify_mock.assert_called_once_with(
        MessageType.ERROR,
        "Error updating queries history.\nSee logs for details.",
    )


# =============================================================================
# SAVE REQUESTED
# =============================================================================


def test_save_requested_refreshes_results_when_updates_succeed(
    workspace,
    execute_updates_mock,
    execute_query_mock,
    notify_mock,
    app_mock,
    mocker,
):
    """
    Verifica que, cuando los UPDATE se ejecutan
    correctamente, se refrescan los resultados y
    se notifica el éxito.
    """

    operations = [MagicMock()]

    workspace.current_query = "SELECT * FROM users"

    workspace.results_view.table.model = MagicMock()
    workspace.results_view.table.model.generate_update_operations.return_value = (
        operations
    )

    script_result = MagicMock()
    script_result.rolled_back = False

    query_result = MagicMock()

    execute_updates_mock.return_value = script_result
    execute_query_mock.return_value = query_result

    mocker.patch.object(workspace.results_view, "show_result")
    mocker.patch.object(workspace.results_view, "set_tab_buttons_state")
    mocker.patch.object(workspace.results_view, "set_action_buttons_state")

    workspace._on_save_requested()

    app_mock.processEvents.assert_called_once()

    execute_updates_mock.assert_called_once_with(
        connection_id=1,
        operations=operations,
    )

    execute_query_mock.assert_called_once_with(
        connection_id=1,
        query="SELECT * FROM users",
    )

    assert workspace.results_view.show_result.call_count == 2

    workspace.results_view.show_result.assert_any_call(
        result=query_result,
        script_result=None,
        is_script=False,
    )

    workspace.results_view.show_result.assert_any_call(
        result=None,
        script_result=script_result,
        is_script=True,
    )

    workspace.results_view.set_action_buttons_state.assert_called_once_with(False)
    workspace.results_view.set_tab_buttons_state.assert_called_once_with(True)

    assert notify_mock.call_args_list == [
        mocker.call(MessageType.WARNING, "Saving changes..."),
        mocker.call(MessageType.SUCCESS, "Changes saved"),
    ]


def test_save_requested_does_not_refresh_results_when_updates_are_rolled_back(
    workspace,
    execute_updates_mock,
    execute_query_mock,
    notify_mock,
    app_mock,
    mocker,
):
    """
    Verifica que, si la transacción hace rollback,
    no se vuelve a ejecutar la consulta original.
    """

    operations = [MagicMock()]

    workspace.current_query = "SELECT * FROM users"

    workspace.results_view.table.model = MagicMock()
    workspace.results_view.table.model.generate_update_operations.return_value = (
        operations
    )

    script_result = MagicMock()
    script_result.rolled_back = True

    execute_updates_mock.return_value = script_result

    mocker.patch.object(workspace.results_view, "show_result")
    mocker.patch.object(workspace.results_view, "set_tab_buttons_state")
    mocker.patch.object(workspace.results_view, "set_action_buttons_state")

    workspace._on_save_requested()

    app_mock.processEvents.assert_called_once()

    execute_updates_mock.assert_called_once_with(
        connection_id=1,
        operations=operations,
    )

    execute_query_mock.assert_not_called()

    workspace.results_view.show_result.assert_called_once_with(
        result=None,
        script_result=script_result,
        is_script=True,
    )

    workspace.results_view.set_action_buttons_state.assert_not_called()
    workspace.results_view.set_tab_buttons_state.assert_called_once_with(True)

    assert notify_mock.call_args_list == [
        mocker.call(MessageType.WARNING, "Saving changes..."),
        mocker.call(MessageType.ERROR, "Saving changes failed."),
    ]


# =============================================================================
# PUBLIC API
# =============================================================================


@pytest.mark.parametrize(
    (
        "count",
        "expected",
    ),
    [
        (0, None),
        (-1, None),
        (3, UnsavedChangesCount),
    ],
)
def test_get_unsaved_changes_count(
    workspace,
    mocker,
    count,
    expected,
):
    """
    Devuelve None cuando no existen cambios pendientes y
    una entidad UnsavedChangesCount cuando sí los hay.
    """

    mocker.patch.object(
        workspace.sql_editor_area,
        "get_unsaved_changes_count",
        return_value=count,
    )

    result = workspace.get_unsaved_changes_count()

    if expected is None:
        assert result is None

    else:
        assert isinstance(result, UnsavedChangesCount)
        assert result.connection_name == workspace.connection.name
        assert result.unsaved_changes == count


# =============================================================================
# SESSION HISTORY
# =============================================================================


def test_query_selected_from_history_sets_editor_text(
    workspace,
    mocker,
):
    """
    Verifica que seleccionar una consulta del historial
    la copia al editor.
    """

    set_query_text = mocker.patch.object(
        workspace.sql_editor_area,
        "set_query_text",
    )

    query = "SELECT * FROM users"

    workspace._on_query_selected_from_session_queries_history(
        query,
    )

    set_query_text.assert_called_once_with(query)


# =============================================================================
# NAVIGATION TREE
# =============================================================================


def test_navigation_tree_insert_sql_sets_editor_text(
    workspace,
    mocker,
):
    """
    Verifica que INSERT_SQL_IN_EDITOR copia el SQL
    al editor.
    """

    set_query_text = mocker.patch.object(
        workspace.sql_editor_area,
        "set_query_text",
    )

    sql = "SELECT * FROM users"

    workspace._on_navigation_tree_action(
        NavigationTreeAction.INSERT_SQL_IN_EDITOR,
        sql,
    )

    set_query_text.assert_called_once_with(sql)


def test_navigation_tree_execute_sql_executes_query(
    workspace,
    mocker,
):
    """
    Verifica que EXECUTE_SQL delega la ejecución
    al flujo habitual de consultas.
    """

    execute_query = mocker.patch.object(
        workspace,
        "_execute_query",
    )

    sql = "SELECT * FROM users"

    workspace._on_navigation_tree_action(
        NavigationTreeAction.EXECUTE_SQL,
        sql,
    )

    execute_query.assert_called_once_with([sql])


# =============================================================================
# SIGNALS
# =============================================================================


def test_connect_signals(
    workspace,
    mocker,
):
    """
    Verifica que todas las señales se conectan
    a sus handlers.
    """

    workspace = Workspace(workspace.connection)

    workspace.sql_editor_area.execute_requested = mocker.Mock()
    workspace.results_view.save_requested = mocker.Mock()
    workspace.results_view.query_selected_from_session_queries_history = mocker.Mock()
    workspace.navigation_tree.action_requested = mocker.Mock()
    workspace.navigation_tree.tree_reloaded = mocker.Mock()

    workspace._connect_signals()

    workspace.sql_editor_area.execute_requested.connect.assert_called_once_with(
        workspace._on_execute_requested,
    )

    workspace.results_view.save_requested.connect.assert_called_once_with(
        workspace._on_save_requested,
    )

    workspace.results_view.query_selected_from_session_queries_history.connect.assert_called_once_with(
        workspace._on_query_selected_from_session_queries_history,
    )

    workspace.navigation_tree.action_requested.connect.assert_called_once_with(
        workspace._on_navigation_tree_action,
    )

    workspace.navigation_tree.tree_reloaded.connect.assert_called_once_with(
        workspace.sql_editor_area.force_update_editors_completers,
    )

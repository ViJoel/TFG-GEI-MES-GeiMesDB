from unittest.mock import (
    MagicMock,
    patch,
)

import pytest

from entities.connection import Connection
from entities.message_type import MessageType
from entities.sql_scope import SqlScope
from entities.unsaved_changes_count import UnsavedChangesCount
from ui.widgets.workspace.workspace import Workspace

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture(autouse=True)
def patch_dependencies():
    with patch("ui.widgets.workspace.results_view.results_view.notify"), patch(
        "ui.widgets.workspace.results_view.results_view.ConfirmationDialog"
    ), patch(
        "ui.widgets.workspace.results_view.connection_queries_history.notify"
    ), patch(
        "ui.widgets.workspace.results_view.connection_queries_history.get_queries_history",
        return_value=[],
    ), patch(
        "ui.widgets.workspace.results_view.connection_queries_history.AppContext.get_task_manager"
    ), patch(
        "ui.widgets.workspace.results_view.connection_queries_history.AppContext.get_app"
    ), patch(
        "ui.widgets.workspace.workspace.notify"
    ):
        yield


@pytest.fixture
def mock_get_app():
    with patch("ui.widgets.workspace.workspace.AppContext.get_app") as mock:
        yield mock


@pytest.fixture
def mock_save():
    with patch("ui.widgets.workspace.workspace.save_queries_history_batch") as mock:
        yield mock


@pytest.fixture
def mock_notify():
    with patch("ui.widgets.workspace.workspace.notify") as mock:
        yield mock


@pytest.fixture
def mock_execute_query():
    with patch("ui.widgets.workspace.workspace.execute_query") as mock:
        yield mock


@pytest.fixture
def mock_execute_script():
    with patch("ui.widgets.workspace.workspace.execute_script") as mock:
        yield mock


@pytest.fixture
def mock_execute_updates():
    with patch("ui.widgets.workspace.workspace.execute_updates") as mock:
        yield mock


@pytest.fixture
def mock_is_editable_query():
    with patch("ui.widgets.workspace.workspace.is_editable_query") as mock:
        yield mock


@pytest.fixture
def connection():
    """
    Crea una conexión simulada para los tests.
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
    Crea una instancia de Workspace y la registra
    en qtbot asegurando que los parches de inicialización
    estén activos.
    """

    widget = Workspace(connection)
    qtbot.addWidget(widget)

    return widget


# =============================================================================
# ON EXECUTE REQUESTED
# =============================================================================


def test_selected_text_executes_query(
    workspace,
):
    """
    Verifica que una solicitud de ejecución sobre
    el texto seleccionado ejecuta una consulta.
    """

    workspace._execute_query = MagicMock()
    workspace._execute_script = MagicMock()
    workspace.results_view.set_action_buttons_state = MagicMock()

    queries = ["SELECT * FROM users"]

    workspace._on_execute_requested(
        queries,
        SqlScope.SELECTED_TEXT,
    )

    workspace._execute_query.assert_called_once_with(queries)
    workspace._execute_script.assert_not_called()

    workspace.results_view.set_action_buttons_state.assert_called_once_with(
        False,
    )


def test_full_script_executes_script(
    workspace,
):
    """
    Verifica que una solicitud de ejecución del
    script completo ejecuta un script SQL.
    """

    workspace._execute_query = MagicMock()
    workspace._execute_script = MagicMock()
    workspace.results_view.set_action_buttons_state = MagicMock()

    queries = [
        "CREATE TABLE test(id INTEGER);",
        "SELECT * FROM test;",
    ]

    workspace._on_execute_requested(
        queries,
        SqlScope.FULL_SCRIPT,
    )

    workspace._execute_script.assert_called_once_with(queries)
    workspace._execute_query.assert_not_called()

    workspace.results_view.set_action_buttons_state.assert_called_once_with(
        False,
    )


def test_execute_requested_adds_query_to_session_history(
    workspace,
):
    """
    Verifica que cada consulta ejecutada se añade
    al historial de consultas de la sesión.
    """

    workspace._execute_query = MagicMock()
    workspace.results_view.add_entry_to_session_queries_history = MagicMock()
    workspace.results_view.set_action_buttons_state = MagicMock()

    queries = ["SELECT * FROM users"]

    workspace._on_execute_requested(
        queries,
        SqlScope.SELECTED_TEXT,
    )

    workspace.results_view.add_entry_to_session_queries_history.assert_called_once()

    call = workspace.results_view.add_entry_to_session_queries_history.call_args
    entry = call.kwargs["entry"]

    assert entry.connection_id == workspace.connection.id
    assert entry.query == "SELECT * FROM users"


def test_execute_requested_adds_all_script_queries_to_session_history(
    workspace,
):
    """
    Verifica que cada sentencia de un script se
    registra individualmente en el historial.
    """

    workspace._execute_script = MagicMock()
    workspace.results_view.add_entry_to_session_queries_history = MagicMock()
    workspace.results_view.set_action_buttons_state = MagicMock()

    queries = [
        "CREATE TABLE test(id INTEGER);",
        "SELECT * FROM test;",
    ]

    workspace._on_execute_requested(
        queries,
        SqlScope.FULL_SCRIPT,
    )

    assert workspace.results_view.add_entry_to_session_queries_history.call_count == 2

    calls = workspace.results_view.add_entry_to_session_queries_history.call_args_list

    assert calls[0].kwargs["entry"].query == queries[0]
    assert calls[1].kwargs["entry"].query == queries[1]


def test_execute_requested_processes_events_and_saves_history(
    mock_get_app,
    workspace,
):
    """
    Debe repintar la UI y guardar el historial
    antes de finalizar la ejecución.
    """

    app = MagicMock()
    mock_get_app.return_value = app

    workspace._execute_query = MagicMock()
    workspace._save_queries_history = MagicMock()
    workspace.results_view.set_action_buttons_state = MagicMock()

    queries = ["SELECT * FROM users"]

    workspace._on_execute_requested(
        queries,
        SqlScope.SELECTED_TEXT,
    )

    app.processEvents.assert_called_once()

    workspace._save_queries_history.assert_called_once_with(queries)


# =============================================================================
# EXECUTE QUERY
# =============================================================================


def test_execute_single_query(
    mock_execute_query,
    mock_is_editable_query,
    workspace,
):
    """
    Verifica que una única consulta se ejecuta y
    actualiza correctamente la vista de resultados.
    """

    result = MagicMock()

    mock_execute_query.return_value = result
    mock_is_editable_query.return_value = True

    workspace.results_view.show_result = MagicMock()
    workspace.results_view.set_editable = MagicMock()

    query = "SELECT * FROM users"

    workspace._execute_query([query])

    assert workspace.current_query == query

    mock_execute_query.assert_called_once_with(
        connection_id=1,
        query=query,
    )

    mock_is_editable_query.assert_called_once_with(query)

    workspace.results_view.show_result.assert_called_once_with(
        result=result,
        script_result=None,
        is_script=False,
    )

    workspace.results_view.set_editable.assert_called_once_with(True)


def test_execute_multiple_queries_aborts_execution(
    mock_execute_query,
    mock_notify,
    workspace,
):
    """
    Verifica que la ejecución se cancela cuando se
    intenta ejecutar más de una consulta como una
    única query.
    """

    workspace.results_view.write_message = MagicMock()
    workspace.results_view.show_console = MagicMock()

    queries = [
        "SELECT * FROM users;",
        "SELECT * FROM products;",
    ]

    workspace._execute_query(queries)

    mock_execute_query.assert_not_called()

    workspace.results_view.write_message.assert_called_once()
    workspace.results_view.show_console.assert_called_once()
    mock_notify.assert_called_once()


# =============================================================================
# EXECUTE SCRIPT
# =============================================================================


def test_execute_script(
    mock_execute_script,
    workspace,
):
    """
    Verifica que un script SQL se ejecuta y que
    los resultados se muestran correctamente.
    """

    script_result = MagicMock()

    mock_execute_script.return_value = script_result

    workspace.results_view.show_result = MagicMock()
    workspace.results_view.set_editable = MagicMock()

    queries = [
        "CREATE TABLE users(id INTEGER);",
        "INSERT INTO users VALUES (1);",
    ]

    workspace._execute_script(queries)

    mock_execute_script.assert_called_once_with(
        connection_id=1,
        queries=queries,
    )

    workspace.results_view.show_result.assert_called_once_with(
        result=None,
        script_result=script_result,
        is_script=True,
    )

    workspace.results_view.set_editable.assert_called_once_with(False)


# =============================================================================
# SAVE REQUESTED
# =============================================================================


def test_save_requested_refreshes_results_when_updates_succeed(
    mock_execute_updates,
    mock_execute_query,
    mock_notify,
    workspace,
):
    """
    Verifica que, si las operaciones UPDATE se
    ejecutan correctamente, se vuelve a ejecutar
    la consulta original y se actualiza la vista.
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

    mock_execute_updates.return_value = script_result
    mock_execute_query.return_value = query_result

    workspace.results_view.show_result = MagicMock()
    workspace.results_view.set_tab_buttons_state = MagicMock()
    workspace.results_view.set_action_buttons_state = MagicMock()

    workspace._on_save_requested()

    workspace.results_view.table.model.generate_update_operations.assert_called_once()

    mock_execute_updates.assert_called_once_with(
        connection_id=1,
        operations=operations,
    )

    mock_execute_query.assert_called_once_with(
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

    mock_notify.assert_called_once_with(
        MessageType.SUCCESS,
        "Changes saved",
    )


def test_save_requested_does_not_refresh_results_when_updates_are_rolled_back(
    mock_execute_updates,
    mock_execute_query,
    mock_notify,
    workspace,
):
    """
    Verifica que, si las operaciones UPDATE
    provocan un rollback, no se vuelve a ejecutar
    la consulta original y se conserva el estado
    actual de la tabla.
    """

    operations = [MagicMock()]

    workspace.current_query = "SELECT * FROM users"

    workspace.results_view.table.model = MagicMock()
    workspace.results_view.table.model.generate_update_operations.return_value = (
        operations
    )

    script_result = MagicMock()
    script_result.rolled_back = True

    mock_execute_updates.return_value = script_result

    workspace.results_view.show_result = MagicMock()
    workspace.results_view.set_tab_buttons_state = MagicMock()
    workspace.results_view.set_action_buttons_state = MagicMock()

    workspace._on_save_requested()

    workspace.results_view.table.model.generate_update_operations.assert_called_once()

    mock_execute_updates.assert_called_once_with(
        connection_id=1,
        operations=operations,
    )

    mock_execute_query.assert_not_called()

    workspace.results_view.show_result.assert_called_once_with(
        result=None,
        script_result=script_result,
        is_script=True,
    )

    workspace.results_view.set_action_buttons_state.assert_not_called()

    workspace.results_view.set_tab_buttons_state.assert_called_once_with(True)

    mock_notify.assert_called_once_with(
        MessageType.ERROR,
        "Saving changes failed.",
    )


# =============================================================================
# ON QUERY SELECTED FROM SESSION QUERIES HISTORY
# =============================================================================


def test_query_selected_from_session_history_updates_editor(
    workspace,
):
    """
    Verifica que seleccionar una consulta del
    historial la inserta en el editor SQL.
    """

    workspace.sql_editor_area.set_query_text = MagicMock()

    query = "SELECT * FROM users"

    workspace._on_query_selected_from_session_queries_history(query)

    workspace.sql_editor_area.set_query_text.assert_called_once_with(
        query,
    )


# =============================================================================
# SAVE QUERIES HISTORY
# =============================================================================


def test_save_queries_history(
    mock_get_app,
    mock_save,
    workspace,
):
    """
    Debe crear las entradas y persistirlas.
    """

    app = MagicMock()
    mock_get_app.return_value = app

    workspace.results_view.add_entry_to_session_queries_history = MagicMock()

    queries = [
        "SELECT 1",
        "SELECT 2",
    ]

    workspace._save_queries_history(queries)

    app.processEvents.assert_called_once()

    assert workspace.results_view.add_entry_to_session_queries_history.call_count == 2

    mock_save.assert_called_once()

    entries = mock_save.call_args.kwargs["entries"]

    assert len(entries) == 2
    assert entries[0].query == "SELECT 1"
    assert entries[1].query == "SELECT 2"


# =============================================================================
# PUBLIC API
# =============================================================================


def test_get_unsaved_changes_count_returns_none_when_there_are_no_changes(workspace):
    workspace.sql_editor_area.get_unsaved_changes_count = MagicMock(return_value=0)

    result = workspace.get_unsaved_changes_count()

    assert result is None


def test_get_unsaved_changes_count_returns_entity(workspace):
    workspace.sql_editor_area.get_unsaved_changes_count = MagicMock(return_value=3)

    result = workspace.get_unsaved_changes_count()

    assert isinstance(result, UnsavedChangesCount)
    assert result.connection_name == workspace.connection.name
    assert result.unsaved_changes == 3


@pytest.mark.parametrize("count", [0, -1])
def test_get_unsaved_changes_count_returns_none_when_there_are_no_changes(
    workspace,
    count,
):
    workspace.sql_editor_area.get_unsaved_changes_count = MagicMock(
        return_value=count,
    )

    assert workspace.get_unsaved_changes_count() is None

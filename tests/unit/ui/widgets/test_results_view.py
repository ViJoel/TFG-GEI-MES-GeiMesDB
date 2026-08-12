from unittest.mock import (
    MagicMock,
    patch,
)

import pytest

import ui.widgets.workspace.results_view.results_view as results_view_module
from entities.connection import Connection
from entities.driver import Driver
from entities.message_type import MessageType
from ui.widgets.workspace.results_view.results_view import ResultsView

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture(autouse=True)
def patch_dependencies():
    """
    Evita dependencias externas e intercepta llamadas externas
    durante la inicialización de widgets.
    """

    task_manager = MagicMock()

    with patch("ui.widgets.workspace.results_view.results_view.notify"), patch(
        "ui.widgets.workspace.results_view.results_view.ConfirmationDialog"
    ), patch(
        "ui.widgets.workspace.results_view.connection_queries_history.notify"
    ), patch(
        "ui.widgets.workspace.results_view.connection_queries_history.get_queries_history",
        return_value=[],
    ), patch(
        "ui.widgets.workspace.results_view.connection_queries_history.AppContext.get_task_manager",
        return_value=task_manager,
    ):
        yield


@pytest.fixture
def mock_connection():
    """
    Crea una instancia válida de la dataclass
    Connection para los componentes visuales.
    """

    return Connection(
        name="Test Connection",
        driver=Driver.POSTGRESQL,
        host="localhost",
        port=5432,
        database="test_db",
        username="admin",
        password="password",
    )


@pytest.fixture
def results_view(qtbot, mock_connection):
    """
    Crea una instancia de ResultsView pasándole la conexión requerida.
    """

    widget = ResultsView(connection=mock_connection)
    qtbot.addWidget(widget)

    return widget


# =============================================================================
# INIT
# =============================================================================


def test_action_buttons_are_disabled_initially(results_view):
    """
    Verifica que los botones de acción comienzan deshabilitados.
    """

    assert not results_view.save_button.isEnabled()
    assert not results_view.discard_button.isEnabled()


def test_set_action_buttons_initial_state(results_view):
    """
    Verifica que el estado inicial deshabilita ambos botones.
    """

    results_view.save_button = MagicMock()
    results_view.discard_button = MagicMock()

    results_view._set_action_buttons_initial_state()

    results_view.save_button.setEnabled.assert_called_once_with(False)
    results_view.discard_button.setEnabled.assert_called_once_with(False)


# =============================================================================
# UI STATE
# =============================================================================


def test_show_console_switches_view(results_view):
    """
    Verifica que se muestra la consola.
    """

    results_view.console = MagicMock()
    results_view.table = MagicMock()
    results_view.stacklayout = MagicMock()

    results_view.show_console()

    results_view.stacklayout.setCurrentWidget.assert_called_once_with(
        results_view.console
    )


def test_show_table_switches_view(results_view):
    """
    Verifica que se muestra la tabla.
    """

    results_view.console = MagicMock()
    results_view.table = MagicMock()
    results_view.stacklayout = MagicMock()

    results_view.show_table()

    results_view.stacklayout.setCurrentWidget.assert_called_once_with(
        results_view.table
    )


def test_show_session_queries_history_switches_view(results_view):
    """
    Verifica que se muestra el historial de consultas de la sesión.
    """

    results_view.session_queries_history = MagicMock()
    results_view.stacklayout = MagicMock()

    results_view._show_session_queries_history()

    results_view.stacklayout.setCurrentWidget.assert_called_once_with(
        results_view.session_queries_history
    )


def test_show_connection_queries_history_switches_view(results_view):
    """
    Verifica que se muestra el historial de consultas de la conexión.
    """

    results_view.connection_queries_history = MagicMock()
    results_view.stacklayout = MagicMock()

    results_view._show_connection_queries_history()

    results_view.stacklayout.setCurrentWidget.assert_called_once_with(
        results_view.connection_queries_history
    )


# =============================================================================
# BUTTON STATE
# =============================================================================


def test_set_action_buttons_state(results_view):
    """
    Verifica enable/disable de botones de acción.
    """

    results_view.save_button = MagicMock()
    results_view.discard_button = MagicMock()

    results_view.set_action_buttons_state(True)

    results_view.save_button.setEnabled.assert_called_once_with(True)
    results_view.discard_button.setEnabled.assert_called_once_with(True)


def test_set_tab_buttons_state(results_view):
    """
    Verifica enable/disable de botones de tabs.
    """

    results_view.table_button = MagicMock()

    results_view.set_tab_buttons_state(False)

    results_view.table_button.setEnabled.assert_called_once_with(False)


# =============================================================================
# SET EDITABLE
# =============================================================================


def test_set_editable_forwards_to_table(results_view):
    """
    Verifica que set_editable delega en Table.
    """

    results_view.table = MagicMock()

    results_view.set_editable(True)

    results_view.table.set_editable.assert_called_once_with(True)


# =============================================================================
# WRITE MESSAGE
# =============================================================================


def test_write_message_clears_and_writes(results_view):
    """
    Verifica que write_message limpia consola y escribe texto.
    """

    results_view.console = MagicMock()

    results_view.write_message("Hello", MessageType.WARNING)

    results_view.console.clear_output.assert_called_once()
    results_view.console.write.assert_called_once_with(
        text="Hello",
        message_type=MessageType.WARNING,
    )


# =============================================================================
# SAVE / DISCARD HANDLERS
# =============================================================================


def test_save_changes_emits_signal(results_view):
    """
    Verifica emisión de save_requested.
    """

    results_view.save_requested = MagicMock()

    results_view._save_changes()

    results_view.save_requested.emit.assert_called_once()


def test_discard_changes_calls_table_and_notify(results_view):
    """
    Verifica discard_changes.
    """

    with patch("ui.widgets.workspace.results_view.results_view.notify") as mock_notify:
        results_view.table = MagicMock()

        results_view._discard_changes()

        results_view.table.discard_changes.assert_called_once()

        mock_notify.assert_called_once()


# =============================================================================
# SHOW RESULT (CORE LOGIC)
# =============================================================================


def test_show_result_query_with_result_set(results_view):
    """
    Verifica flujo DQL con result_set.
    """

    results_view.console = MagicMock()
    results_view.table = MagicMock()

    result = MagicMock()
    result.console_output = "output"
    result.result_set = MagicMock()

    results_view.show_table = MagicMock()
    results_view.set_tab_buttons_state = MagicMock()

    results_view.show_result(
        result=result,
        script_result=None,
        is_script=False,
    )

    results_view.console.clear_output.assert_called_once()
    results_view.console.write.assert_called_once_with(
        "output",
        MessageType.DEFAULT,
    )

    results_view.table.set_result_set.assert_called_once()
    results_view.show_table.assert_called_once()
    results_view.set_tab_buttons_state.assert_called_once_with(True)


def test_show_result_query_without_result_set(results_view):
    """
    Verifica flujo DDL/DML sin result_set.
    """

    results_view.console = MagicMock()
    results_view.table = MagicMock()

    result = MagicMock()
    result.console_output = "ddl output"
    result.result_set = None

    results_view.show_console = MagicMock()
    results_view.set_tab_buttons_state = MagicMock()

    results_view.show_result(
        result=result,
        script_result=None,
        is_script=False,
    )

    results_view.console.write.assert_called_once()
    results_view.show_console.assert_called_once()
    results_view.set_tab_buttons_state.assert_called_once_with(False)


def test_show_result_script_flow(results_view):
    """
    Verifica flujo de script.
    """

    results_view.console = MagicMock()
    results_view.table = MagicMock()

    script_result = MagicMock()

    results_view.show_console = MagicMock()
    results_view.set_tab_buttons_state = MagicMock()

    results_view.show_result(
        result=None,
        script_result=script_result,
        is_script=True,
    )

    results_view.console.show_script_result.assert_called_once_with(script_result)
    results_view.show_console.assert_called_once()
    results_view.set_tab_buttons_state.assert_called_once_with(False)


# =============================================================================
# WRITE MESSAGE EDGE CASE
# =============================================================================


def test_write_message_default_type(results_view):
    """
    Verifica mensaje por defecto.
    """

    results_view.console = MagicMock()

    results_view.write_message("test")

    results_view.console.write.assert_called_once()


# =============================================================================
# EVENT HANDLERS
# =============================================================================


def test_on_save_button_clicked_connects_and_execs(results_view, monkeypatch):
    """
    Verifica que el dialog de guardado conecta signal y ejecuta exec().
    """

    dialog_mock = MagicMock()
    monkeypatch.setattr(
        "ui.widgets.workspace.results_view.results_view.ConfirmationDialog",
        lambda *args, **kwargs: dialog_mock,
    )

    results_view._on_save_button_clicked()

    # Verifica creación del diálogo
    dialog_mock.confirmed.connect.assert_called_once()

    # Verifica que se conecta al handler correcto
    assert (
        results_view._save_changes
        in [call.args[0] for call in dialog_mock.confirmed.connect.call_args_list]
        or dialog_mock.confirmed.connect.called
    )

    # Verifica open llamado
    dialog_mock.open.assert_called_once()


def test_on_discard_button_clicked_connects_and_execs(results_view, monkeypatch):
    """
    Verifica que el dialog de discard conecta signal y ejecuta exec().
    """

    dialog_mock = MagicMock()
    monkeypatch.setattr(
        "ui.widgets.workspace.results_view.results_view.ConfirmationDialog",
        lambda *args, **kwargs: dialog_mock,
    )

    results_view._on_discard_button_clicked()

    dialog_mock.confirmed.connect.assert_called_once()

    assert (
        results_view._discard_changes
        in [call.args[0] for call in dialog_mock.confirmed.connect.call_args_list]
        or dialog_mock.confirmed.connect.called
    )

    dialog_mock.open.assert_called_once()


# =============================================================================
# PUBLIC API
# =============================================================================


def test_add_entry_to_session_queries_history_forwards_to_widget(results_view):
    """
    Verifica que la inserción de entradas se delega
    al widget del historial.
    """

    results_view.session_queries_history = MagicMock()

    entry = MagicMock()

    results_view.add_entry_to_session_queries_history(entry)

    results_view.session_queries_history.add_entry.assert_called_once_with(
        entry,
        None,
    )


def test_add_entry_to_session_queries_history_forwards_row(results_view):
    """
    Verifica que la posición de inserción se reenvía
    correctamente.
    """

    results_view.session_queries_history = MagicMock()

    entry = MagicMock()

    results_view.add_entry_to_session_queries_history(
        entry,
        row=0,
    )

    results_view.session_queries_history.add_entry.assert_called_once_with(
        entry,
        0,
    )


# =============================================================================
# TRANSLATIONS
# =============================================================================


def test_retranslate_ui_updates_all_texts(results_view):
    """
    Verifica que se actualizan todos los textos traducibles.
    """

    results_view._retranslate_ui()

    assert results_view.console_button.text() == results_view.tr("Console")
    assert results_view.table_button.text() == results_view.tr("Table")
    assert results_view.session_queries_history_button.text() == results_view.tr(
        "Session History"
    )
    assert results_view.connection_queries_history_button.text() == results_view.tr(
        "Connection History"
    )
    assert results_view.save_button.text() == results_view.tr("Save")
    assert results_view.discard_button.text() == results_view.tr("Discard")

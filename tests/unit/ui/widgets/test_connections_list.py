import logging
from unittest.mock import MagicMock

import pytest
from PySide6.QtCore import Qt

from entities.connection import Connection
from entities.driver import Driver
from entities.message_type import MessageType
from ui.widgets.sidebar.connections_list import ConnectionsList

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def connection():
    return Connection(
        id=1,
        name="Local",
        driver=Driver.POSTGRESQL,
        host="localhost",
        port=5432,
        database="db",
        username="user",
        password="pass",
    )


@pytest.fixture
def connections(monkeypatch, connection):
    monkeypatch.setattr(
        "ui.widgets.sidebar.connections_list.get_connections",
        lambda: [connection],
    )
    return [connection]


@pytest.fixture
def widget(qtbot, connections):
    w = ConnectionsList()
    qtbot.addWidget(w)
    return w


@pytest.fixture(autouse=True)
def patch_logger_success(monkeypatch):
    """
    Evita fallos por logger.success.
    """

    logger = logging.getLogger("ui.widgets.sidebar.connections_list")
    monkeypatch.setattr(logger, "success", logger.info, raising=False)


# =============================================================================
# INITIALIZATION
# =============================================================================


def test_widget_is_created(widget):
    assert widget.list_widget is not None

    assert widget.add_button is not None
    assert widget.edit_button is not None
    assert widget.delete_button is not None
    assert widget.connect_button is not None
    assert widget.disconnect_button is not None


def test_initial_buttons_state(widget):
    assert widget.add_button.isEnabled()

    assert not widget.edit_button.isEnabled()
    assert not widget.delete_button.isEnabled()
    assert not widget.connect_button.isEnabled()
    assert not widget.disconnect_button.isEnabled()


def test_connections_are_loaded(widget):
    assert widget.list_widget.count() == 1


# =============================================================================
# UI HELPERS
# =============================================================================


def test_create_icon_button(widget):
    button = widget._create_icon_button(
        "fa5s.plus",
        "test",
    )

    assert button.objectName() == "test"
    assert button.width() == 32
    assert button.height() == 32


def test_add_connection_item(widget, connection):
    widget.list_widget.clear()

    widget._add_connection_item(connection)

    assert widget.list_widget.count() == 1

    item = widget.list_widget.item(0)

    assert item.data(Qt.ItemDataRole.UserRole) == connection


def test_get_selected_connection_returns_none(widget):
    widget.list_widget.clearSelection()
    widget.list_widget.setCurrentItem(None)

    assert widget._get_selected_connection() is None


def test_get_selected_connection_returns_connection(widget, connection):
    widget.list_widget.setCurrentRow(0)

    assert widget._get_selected_connection() == connection


# =============================================================================
# UI STATE
# =============================================================================


def test_setup_buttons_state(widget):
    """
    Verifica el estado inicial de los botones.
    """

    widget.edit_button.setEnabled(True)
    widget.delete_button.setEnabled(True)
    widget.connect_button.setEnabled(True)
    widget.disconnect_button.setEnabled(True)

    widget._setup_buttons_state()

    assert widget.add_button.isEnabled()
    assert not widget.edit_button.isEnabled()
    assert not widget.delete_button.isEnabled()
    assert not widget.connect_button.isEnabled()
    assert not widget.disconnect_button.isEnabled()


def test_update_buttons_state_without_selection(widget):
    """
    Verifica el estado de los botones cuando no hay selección.
    """

    widget._update_buttons_state(None)

    assert not widget.edit_button.isEnabled()
    assert not widget.delete_button.isEnabled()
    assert not widget.connect_button.isEnabled()
    assert not widget.disconnect_button.isEnabled()


def test_update_buttons_state_disconnected(
    monkeypatch,
    widget,
    connection,
):
    """
    Verifica el estado de los botones con una conexión desconectada.
    """

    monkeypatch.setattr(
        "ui.widgets.sidebar.connections_list.has_session",
        lambda _: False,
    )

    widget._update_buttons_state(connection)

    assert widget.edit_button.isEnabled()
    assert widget.delete_button.isEnabled()
    assert widget.connect_button.isEnabled()
    assert not widget.disconnect_button.isEnabled()


def test_update_buttons_state_connected(
    monkeypatch,
    widget,
    connection,
):
    """
    Verifica el estado de los botones con una conexión conectada.
    """

    monkeypatch.setattr(
        "ui.widgets.sidebar.connections_list.has_session",
        lambda _: True,
    )

    widget._update_buttons_state(connection)

    assert widget.edit_button.isEnabled()
    assert widget.delete_button.isEnabled()
    assert not widget.connect_button.isEnabled()
    assert widget.disconnect_button.isEnabled()


def test_clear_selection(monkeypatch, widget):
    """
    Verifica que la selección actual se elimina.
    """

    selected = MagicMock()

    monkeypatch.setattr(
        "ui.widgets.sidebar.connections_list.set_selected_connection",
        selected,
    )

    widget.list_widget.setCurrentRow(0)

    selected.reset_mock()

    widget._clear_selection()

    assert widget.list_widget.currentItem() is None
    assert not widget.list_widget.selectedItems()


def test_update_items_selection_state(widget):
    """
    Verifica que el estado visual de los items se actualiza.
    """

    widget.list_widget.setCurrentRow(0)

    item = widget.list_widget.item(0)
    item_widget = widget.list_widget.itemWidget(item)

    item_widget.set_selected = MagicMock()

    widget._update_items_selection_state()

    item_widget.set_selected.assert_called_once_with(True)


def test_sync_selection_state(
    monkeypatch,
    widget,
    connection,
):
    """
    Verifica que el estado de selección se sincroniza correctamente.
    """

    set_selected = MagicMock()
    update_buttons = MagicMock()
    update_items = MagicMock()

    monkeypatch.setattr(
        "ui.widgets.sidebar.connections_list.set_selected_connection",
        set_selected,
    )

    widget._update_buttons_state = update_buttons
    widget._update_items_selection_state = update_items

    widget._sync_selection_state(connection)

    set_selected.assert_called_once_with(connection)
    update_buttons.assert_called_once_with(connection)
    update_items.assert_called_once()


# =============================================================================
# EVENT HANDLERS
# =============================================================================


def test_on_selection_changed_with_selection(widget, connection):
    """
    Verifica que seleccionar una conexión sincroniza el estado
    y emite la señal correspondiente.
    """

    widget._sync_selection_state = MagicMock()

    emitted = []
    widget.connection_selected.connect(emitted.append)

    widget.list_widget.setCurrentRow(0)

    widget._sync_selection_state.assert_called_once_with(connection)
    assert emitted == [connection]


def test_on_selection_changed_without_selection(widget):
    """
    Verifica que sin selección únicamente se sincroniza el estado.
    """

    widget._sync_selection_state = MagicMock()

    emitted = MagicMock()

    widget.connection_selected.connect(emitted)

    widget.list_widget.clearSelection()
    widget.list_widget.setCurrentItem(None)

    widget._on_selection_changed()

    widget._sync_selection_state.assert_called_once_with(None)

    emitted.assert_not_called()


def test_on_add_button_clicked(widget):
    """
    Verifica que solicitar una nueva conexión emite la señal.
    """

    emitted = MagicMock()

    widget.add_connection_requested.connect(emitted)

    widget._on_add_button_clicked()

    emitted.assert_called_once_with()


def test_on_edit_button_clicked_without_selection(widget):
    """
    Verifica que no ocurre nada si no hay conexión seleccionada.
    """

    widget.list_widget.clearSelection()
    widget.list_widget.setCurrentItem(None)

    emitted = MagicMock()

    widget.edit_connection_requested.connect(emitted)

    widget._close_session_if_needed = MagicMock()

    widget._on_edit_button_clicked()

    emitted.assert_not_called()
    widget._close_session_if_needed.assert_not_called()


def test_on_edit_button_clicked(widget, connection):
    """
    Verifica que editar una conexión cierra la sesión si es necesario
    y emite la señal correspondiente.
    """

    widget.list_widget.setCurrentRow(0)

    widget._close_session_if_needed = MagicMock()

    emitted = []

    widget.edit_connection_requested.connect(emitted.append)

    widget._on_edit_button_clicked()

    widget._close_session_if_needed.assert_called_once_with(connection)

    assert emitted == [connection]


def test_on_connect_button_clicked_without_selection(widget):
    """
    Verifica que no se emite ninguna señal sin selección.
    """

    widget.list_widget.clearSelection()
    widget.list_widget.setCurrentItem(None)

    emitted = MagicMock()

    widget.connection_open_requested.connect(emitted)

    widget._on_connect_button_clicked()

    emitted.assert_not_called()


def test_on_connect_button_clicked(widget, connection):
    """
    Verifica que solicitar una conexión emite la señal adecuada.
    """

    widget.list_widget.setCurrentRow(0)

    emitted = []

    widget.connection_open_requested.connect(emitted.append)

    widget._on_connect_button_clicked()

    assert emitted == [connection]


def test_on_disconnect_button_clicked_without_selection(widget):
    """
    Verifica que no se emite ninguna señal sin selección.
    """

    widget.list_widget.clearSelection()
    widget.list_widget.setCurrentItem(None)

    emitted = MagicMock()

    widget.connection_close_requested.connect(emitted)

    widget._on_disconnect_button_clicked()

    emitted.assert_not_called()


def test_on_disconnect_button_clicked(widget, connection):
    """
    Verifica que solicitar el cierre de sesión emite la señal adecuada.
    """

    widget.list_widget.setCurrentRow(0)

    emitted = []

    widget.connection_close_requested.connect(emitted.append)

    widget._on_disconnect_button_clicked()

    assert emitted == [connection]


def test_on_delete_button_clicked_without_selection(widget):
    """
    Verifica que no se abre el diálogo si no existe selección.
    """

    widget.list_widget.clearSelection()
    widget.list_widget.setCurrentItem(None)

    widget._on_delete_button_clicked()

    # El test pasa simplemente si no lanza excepciones.


def test_on_delete_button_clicked_opens_confirmation_dialog(
    monkeypatch,
    widget,
    connection,
):
    """
    Verifica que se crea el diálogo de confirmación.
    """

    widget.list_widget.setCurrentRow(0)

    confirmed = MagicMock()

    dialog = MagicMock()
    dialog.confirmed.connect = confirmed

    dialog_cls = MagicMock(return_value=dialog)

    monkeypatch.setattr(
        "ui.widgets.sidebar.connections_list.ConfirmationDialog",
        dialog_cls,
    )

    widget._on_delete_button_clicked()

    dialog_cls.assert_called_once()

    dialog.exec.assert_called_once()


def test_on_delete_button_clicked_connects_confirmation(
    monkeypatch,
    widget,
    connection,
):
    """
    Verifica que la confirmación ejecuta el borrado.
    """

    widget.list_widget.setCurrentRow(0)

    callback = None

    class FakeSignal:
        def connect(self, fn):
            nonlocal callback
            callback = fn

    class FakeDialog:
        def __init__(self, *_, **__):
            self.confirmed = FakeSignal()

        def exec(self):
            pass

    monkeypatch.setattr(
        "ui.widgets.sidebar.connections_list.ConfirmationDialog",
        FakeDialog,
    )

    delete = MagicMock()

    widget._close_and_delete_connection = delete

    widget._on_delete_button_clicked()

    assert callback is not None

    callback()

    delete.assert_called_once_with(connection)


# =============================================================================
# EVENT HELPERS
# =============================================================================


def test_close_and_delete_connection(widget, connection):
    """
    Verifica que se cierra la sesión antes de eliminar la conexión.
    """

    widget._close_session_if_needed = MagicMock()
    widget._delete_connection = MagicMock()

    widget._close_and_delete_connection(connection)

    widget._close_session_if_needed.assert_called_once_with(connection)
    widget._delete_connection.assert_called_once_with(connection)


def test_delete_connection_success(
    monkeypatch,
    widget,
    connection,
):
    """
    Verifica que una conexión se elimina correctamente.
    """

    try:
        delete = MagicMock()
        notify = MagicMock()
        reload_connections = MagicMock()
        clear_selection = MagicMock()

        monkeypatch.setattr(
            "ui.widgets.sidebar.connections_list.delete_connection",
            delete,
        )

        monkeypatch.setattr(
            "ui.widgets.sidebar.connections_list.notify",
            notify,
        )

        widget.reload_connections = reload_connections
        widget._clear_selection = clear_selection

        widget._delete_connection(connection)

        delete.assert_called_once_with(connection)

        notify.assert_called_once_with(
            MessageType.SUCCESS,
            "Connection deleted",
        )

        reload_connections.assert_called_once()
        clear_selection.assert_called_once()

    except Exception as e:
        print(type(e))
        print(e)
        raise


def test_delete_connection_failure(
    monkeypatch,
    widget,
    connection,
):
    """
    Verifica que un error al eliminar una conexión
    muestra una notificación de error.
    """

    monkeypatch.setattr(
        "ui.widgets.sidebar.connections_list.delete_connection",
        MagicMock(side_effect=Exception("Boom")),
    )

    notify = MagicMock()

    monkeypatch.setattr(
        "ui.widgets.sidebar.connections_list.notify",
        notify,
    )

    widget.reload_connections = MagicMock()
    widget._clear_selection = MagicMock()

    widget._delete_connection(connection)

    notify.assert_called_once_with(
        MessageType.ERROR,
        "Error deleting",
    )

    widget.reload_connections.assert_not_called()
    widget._clear_selection.assert_not_called()


# =============================================================================
# PRIVATE API
# =============================================================================


def test_close_session_if_needed_when_connected(
    monkeypatch,
    widget,
    connection,
):
    """
    Verifica que se solicita cerrar la sesión
    cuando existe una sesión activa.
    """

    monkeypatch.setattr(
        "ui.widgets.sidebar.connections_list.has_session",
        lambda _: True,
    )

    emitted = []

    widget.connection_close_requested.connect(emitted.append)

    widget._close_session_if_needed(connection)

    assert emitted == [connection]


def test_close_session_if_needed_when_disconnected(
    monkeypatch,
    widget,
    connection,
):
    """
    Verifica que no se solicita cerrar la sesión
    cuando no existe una sesión activa.
    """

    monkeypatch.setattr(
        "ui.widgets.sidebar.connections_list.has_session",
        lambda _: False,
    )

    emitted = MagicMock()

    widget.connection_close_requested.connect(emitted)

    widget._close_session_if_needed(connection)

    emitted.assert_not_called()


# =============================================================================
# PUBLIC API
# =============================================================================


def test_reload_connections(widget):
    """
    Verifica que recargar conexiones reconstruye la lista.
    """

    widget._load_connections = MagicMock()

    widget.reload_connections()

    widget._load_connections.assert_called_once()


def test_reload_connections_restores_selected_connection(
    monkeypatch,
    widget,
    connection,
):
    """
    Verifica que al recargar se restaura la conexión seleccionada.
    """

    widget.list_widget.setCurrentRow(0)

    sync = MagicMock()
    widget._sync_selection_state = sync

    widget.reload_connections()

    sync.assert_called_once_with(connection)

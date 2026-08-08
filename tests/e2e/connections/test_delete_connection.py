from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot

from modules.connections.model import get_all_connections
from ui.app.main_window import MainWindow
from ui.widgets.dialogs.confirmation_dialog import ConfirmationDialog

# =============================================================================
# VARIABLES
# =============================================================================

_INITIAL_CONNECTIONS = 4
_CONNECTIONS_AFTER_DELETE = 3

# =============================================================================
# FUNCTIONS
# =============================================================================


def _get_connection_item(
    window: MainWindow,
    connection_name: str,
):
    """
    Obtiene el item y la conexión asociada a partir del nombre.

    Args:
        window (MainWindow):
            Ventana principal que contiene la lista de conexiones.

        connection_name (str):
            Nombre de la conexión que se desea localizar.

    Returns:
        tuple:
            Item de la lista y objeto Connection asociado.

    Raises:
        AssertionError:
            Si no existe ninguna conexión con el nombre indicado.
    """

    list_widget = window.sidebar.connections_list.list_widget

    for index in range(list_widget.count()):

        item = list_widget.item(index)

        connection = item.data(
            Qt.ItemDataRole.UserRole,
        )

        if connection.name == connection_name:
            return item, connection

    raise AssertionError(
        f"Connection '{connection_name}' not found in the connections list."
    )


def _open_delete_dialog(
    qtbot: QtBot,
    window: MainWindow,
    connection_name: str,
) -> ConfirmationDialog:
    """
    Selecciona una conexión y abre el diálogo de confirmación
    para eliminarla.

    Args:
        qtbot (QtBot):
            Fixture de pytest-qt utilizada para interactuar con
            la interfaz gráfica.

        window (MainWindow):
            Ventana principal de la aplicación.

        connection_name (str):
            Nombre de la conexión que se desea eliminar.

    Returns:
        ConfirmationDialog:
            Diálogo de confirmación abierto.
    """

    list_widget = window.sidebar.connections_list.list_widget

    item, connection = _get_connection_item(
        window,
        connection_name,
    )

    list_widget.setCurrentItem(item)

    assert list_widget.currentItem() is item

    delete_button = window.sidebar.connections_list.delete_button

    assert delete_button.isEnabled()

    delete_button.click()

    dialog = window.findChild(
        ConfirmationDialog,
        "confirmation_dialog",
    )

    assert dialog is not None
    assert dialog.isVisible()

    return dialog


# =============================================================================
# TESTS
# =============================================================================


def test_delete_sqlite_connection(
    qtbot: QtBot,
    main_window: MainWindow,
):
    """
    Verifica que se puede eliminar correctamente una conexión SQLite.
    """

    dialog = _open_delete_dialog(
        qtbot,
        main_window,
        "1 - E2E SQLite",
    )

    dialog.accept_button.click()

    connections = get_all_connections()

    assert len(connections) == _CONNECTIONS_AFTER_DELETE

    assert not any(connection.id == "1-e2e-sqlite" for connection in connections)

    assert (
        main_window.sidebar.connections_list.list_widget.count()
        == _CONNECTIONS_AFTER_DELETE
    )


def test_delete_mysql_connection(
    qtbot: QtBot,
    main_window: MainWindow,
):
    """
    Verifica que se puede eliminar correctamente una conexión MySQL.
    """

    dialog = _open_delete_dialog(
        qtbot,
        main_window,
        "1 - E2E MySQL",
    )

    dialog.accept_button.click()

    connections = get_all_connections()

    assert len(connections) == _CONNECTIONS_AFTER_DELETE

    assert not any(connection.id == "1-e2e-mysql" for connection in connections)

    assert (
        main_window.sidebar.connections_list.list_widget.count()
        == _CONNECTIONS_AFTER_DELETE
    )


def test_delete_postgresql_connection(
    qtbot: QtBot,
    main_window: MainWindow,
):
    """
    Verifica que se puede eliminar correctamente una conexión PostgreSQL.
    """

    dialog = _open_delete_dialog(
        qtbot,
        main_window,
        "1 - E2E PostgreSQL",
    )

    dialog.accept_button.click()

    connections = get_all_connections()

    assert len(connections) == _CONNECTIONS_AFTER_DELETE

    assert not any(connection.id == "1-e2e-postgresql" for connection in connections)

    assert (
        main_window.sidebar.connections_list.list_widget.count()
        == _CONNECTIONS_AFTER_DELETE
    )


def test_delete_oracle_connection(
    qtbot: QtBot,
    main_window: MainWindow,
):
    """
    Verifica que se puede eliminar correctamente una conexión Oracle.
    """

    dialog = _open_delete_dialog(
        qtbot,
        main_window,
        "1 - E2E Oracle",
    )

    dialog.accept_button.click()

    connections = get_all_connections()

    assert len(connections) == _CONNECTIONS_AFTER_DELETE

    assert not any(connection.id == "1-e2e-oracle" for connection in connections)

    assert (
        main_window.sidebar.connections_list.list_widget.count()
        == _CONNECTIONS_AFTER_DELETE
    )


def test_cancel_delete_connection(
    qtbot: QtBot,
    main_window: MainWindow,
):
    """
    Verifica que cancelar el diálogo no elimina la conexión seleccionada.
    """

    dialog = _open_delete_dialog(
        qtbot,
        main_window,
        "1 - E2E SQLite",
    )

    dialog.cancel_button.click()

    connections = get_all_connections()

    assert len(connections) == _INITIAL_CONNECTIONS

    assert any(connection.id == "1-e2e-sqlite" for connection in connections)

    assert (
        main_window.sidebar.connections_list.list_widget.count() == _INITIAL_CONNECTIONS
    )

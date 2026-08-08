from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot

from entities.driver import Driver
from modules.connections.model import get_all_connections
from ui.app.main_window import MainWindow

# =============================================================================
# VARIABLES
# =============================================================================

_INITIAL_CONNECTIONS = 4

# =============================================================================
# FUNCTIONS
# =============================================================================


def _open_connection_form(
    qtbot: QtBot,
    window: MainWindow,
    connection_name: str,
):
    """
    Abre el formulario de edición de una conexión existente.

    Localiza una conexión por su nombre dentro de la lista de
    conexiones, la selecciona y abre el formulario de edición
    mediante el botón correspondiente.

    Args:
        qtbot (QtBot):
            Fixture de pytest-qt utilizada para interactuar con
            la interfaz gráfica durante los tests.

        window (MainWindow):
            Ventana principal de la aplicación sobre la que se
            realizará la interacción.

        connection_name (str):
            Nombre de la conexión que se desea seleccionar
            y editar.

    Returns:
        tuple:
            Formulario de conexión actualmente mostrado y objeto
            Connection asociado al item seleccionado.

    Raises:
        AssertionError:
            Si no existe ninguna conexión con el nombre indicado
            o si el botón de edición no está disponible.
    """

    list_widget = window.sidebar.connections_list.list_widget

    item = _get_connection_item(
        window,
        connection_name,
    )

    connection = item.data(
        Qt.ItemDataRole.UserRole,
    )

    list_widget.setCurrentItem(item)

    assert list_widget.currentItem() is item

    edit_button = window.sidebar.connections_list.edit_button

    assert edit_button is not None
    assert edit_button.isEnabled()

    edit_button.click()

    assert window.stack.currentWidget() is window.connection_form_page

    return window.connection_form, connection


def _get_connection_item(
    window: MainWindow,
    connection_name: str,
):
    """
    Obtiene el item de la lista correspondiente a una conexión.

    Args:
        window (MainWindow):
            Ventana principal que contiene la lista de conexiones.

        connection_name (str):
            Nombre de la conexión que se desea localizar.

    Returns:
        QListWidgetItem:
            Item asociado a la conexión solicitada.

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
            return item

    raise AssertionError(
        f"Connection '{connection_name}' not found in the connections list."
    )


# =============================================================================
# TESTS
# =============================================================================


def test_update_sqlite_connection_success(
    qtbot: QtBot,
    main_window: MainWindow,
):
    """
    Verifica que se actualiza correctamente una conexión SQLite válida.
    """

    form, connection = _open_connection_form(
        qtbot,
        main_window,
        "1 - E2E SQLite",
    )

    assert form.name_input.text() == connection.name
    assert form.driver_input.currentText() == connection.driver.value
    assert form.path_input.text() == connection.path

    form.name_input.setText("Updated SQLite connection")
    form.path_input.setText("/tmp/updated-database.db")

    form.save_button.click()

    connections = get_all_connections()

    assert len(connections) == _INITIAL_CONNECTIONS

    updated_connection = next(
        connection for connection in connections if connection.id == "1-e2e-sqlite"
    )

    assert updated_connection.name == "Updated SQLite connection"
    assert updated_connection.driver == Driver.SQLITE
    assert updated_connection.path == "/tmp/updated-database.db"

    assert main_window.stack.currentWidget() is main_window.home_page

    assert (
        main_window.sidebar.connections_list.list_widget.count() == _INITIAL_CONNECTIONS
    )


def test_update_sqlite_connection_invalid_data(
    qtbot: QtBot,
    main_window: MainWindow,
):
    """
    Verifica que no se actualiza una conexión SQLite con datos inválidos.
    """

    form, connection = _open_connection_form(
        qtbot,
        main_window,
        "1 - E2E SQLite",
    )

    assert form.name_input.text() == connection.name
    assert form.driver_input.currentText() == connection.driver.value
    assert form.path_input.text() == connection.path

    form.name_input.clear()
    form.path_input.clear()

    form.save_button.click()

    assert len(get_all_connections()) == _INITIAL_CONNECTIONS

    persisted_connection = next(
        connection
        for connection in get_all_connections()
        if connection.id == "1-e2e-sqlite"
    )

    assert persisted_connection == connection

    assert main_window.stack.currentWidget() is main_window.connection_form_page

    assert (
        main_window.sidebar.connections_list.list_widget.count() == _INITIAL_CONNECTIONS
    )


def test_update_postgresql_connection_success(
    qtbot: QtBot,
    main_window: MainWindow,
):
    """
    Verifica que se actualiza correctamente una conexión PostgreSQL válida.
    """

    form, connection = _open_connection_form(
        qtbot,
        main_window,
        "1 - E2E PostgreSQL",
    )

    assert form.name_input.text() == connection.name
    assert form.driver_input.currentText() == connection.driver.value
    assert form.host_input.text() == connection.host
    assert form.port_input.text() == str(connection.port)
    assert form.database_input.text() == connection.database
    assert form.username_input.text() == connection.username
    assert form.password_input.text() == connection.password

    form.name_input.setText("Updated PostgreSQL connection")
    form.host_input.setText("127.0.0.1")
    form.port_input.setText("5433")
    form.database_input.setText("updated-tfg-test")
    form.username_input.setText("updated-user")
    form.password_input.setText("updated-password")

    form.save_button.click()

    connections = get_all_connections()

    assert len(connections) == _INITIAL_CONNECTIONS

    updated_connection = next(
        connection for connection in connections if connection.id == "1-e2e-postgresql"
    )

    assert updated_connection.name == "Updated PostgreSQL connection"
    assert updated_connection.driver == Driver.POSTGRESQL
    assert updated_connection.host == "127.0.0.1"
    assert updated_connection.port == 5433
    assert updated_connection.database == "updated-tfg-test"
    assert updated_connection.username == "updated-user"
    assert updated_connection.password == "updated-password"

    assert main_window.stack.currentWidget() is main_window.home_page

    assert (
        main_window.sidebar.connections_list.list_widget.count() == _INITIAL_CONNECTIONS
    )


def test_update_postgresql_connection_invalid_data(
    qtbot: QtBot,
    main_window: MainWindow,
):
    """
    Verifica que no se actualiza una conexión PostgreSQL con datos inválidos.
    """

    form, connection = _open_connection_form(
        qtbot,
        main_window,
        "1 - E2E PostgreSQL",
    )

    assert form.name_input.text() == connection.name
    assert form.driver_input.currentText() == connection.driver.value
    assert form.host_input.text() == connection.host
    assert form.port_input.text() == str(connection.port)
    assert form.database_input.text() == connection.database
    assert form.username_input.text() == connection.username
    assert form.password_input.text() == connection.password

    form.name_input.clear()
    form.host_input.clear()
    form.port_input.clear()
    form.database_input.clear()
    form.username_input.clear()
    form.password_input.clear()

    form.save_button.click()

    assert len(get_all_connections()) == _INITIAL_CONNECTIONS

    persisted_connection = next(
        connection
        for connection in get_all_connections()
        if connection.id == "1-e2e-postgresql"
    )

    assert persisted_connection == connection

    assert main_window.stack.currentWidget() is main_window.connection_form_page

    assert (
        main_window.sidebar.connections_list.list_widget.count() == _INITIAL_CONNECTIONS
    )


def test_update_mysql_connection_success(
    qtbot: QtBot,
    main_window: MainWindow,
):
    """
    Verifica que se actualiza correctamente una conexión MySQL válida.
    """

    form, connection = _open_connection_form(
        qtbot,
        main_window,
        "1 - E2E MySQL",
    )

    assert form.name_input.text() == connection.name
    assert form.driver_input.currentText() == connection.driver.value
    assert form.host_input.text() == connection.host
    assert form.port_input.text() == str(connection.port)
    assert form.database_input.text() == connection.database
    assert form.username_input.text() == connection.username
    assert form.password_input.text() == connection.password

    form.name_input.setText("Updated MySQL connection")
    form.host_input.setText("127.0.0.1")
    form.port_input.setText("3307")
    form.database_input.setText("updated-tfg-test")
    form.username_input.setText("updated-user")
    form.password_input.setText("updated-password")

    form.save_button.click()

    connections = get_all_connections()

    assert len(connections) == _INITIAL_CONNECTIONS

    updated_connection = next(
        connection for connection in connections if connection.id == "1-e2e-mysql"
    )

    assert updated_connection.name == "Updated MySQL connection"
    assert updated_connection.driver == Driver.MYSQL
    assert updated_connection.host == "127.0.0.1"
    assert updated_connection.port == 3307
    assert updated_connection.database == "updated-tfg-test"
    assert updated_connection.username == "updated-user"
    assert updated_connection.password == "updated-password"

    assert main_window.stack.currentWidget() is main_window.home_page

    assert (
        main_window.sidebar.connections_list.list_widget.count() == _INITIAL_CONNECTIONS
    )


def test_update_mysql_connection_invalid_data(
    qtbot: QtBot,
    main_window: MainWindow,
):
    """
    Verifica que no se actualiza una conexión MySQL con datos inválidos.
    """

    form, connection = _open_connection_form(
        qtbot,
        main_window,
        "1 - E2E MySQL",
    )

    assert form.name_input.text() == connection.name
    assert form.driver_input.currentText() == connection.driver.value
    assert form.host_input.text() == connection.host
    assert form.port_input.text() == str(connection.port)
    assert form.database_input.text() == connection.database
    assert form.username_input.text() == connection.username
    assert form.password_input.text() == connection.password

    form.name_input.clear()
    form.host_input.clear()
    form.port_input.clear()
    form.database_input.clear()
    form.username_input.clear()
    form.password_input.clear()

    form.save_button.click()

    assert len(get_all_connections()) == _INITIAL_CONNECTIONS

    persisted_connection = next(
        connection
        for connection in get_all_connections()
        if connection.id == "1-e2e-mysql"
    )

    assert persisted_connection == connection

    assert main_window.stack.currentWidget() is main_window.connection_form_page

    assert (
        main_window.sidebar.connections_list.list_widget.count() == _INITIAL_CONNECTIONS
    )


def test_update_oracle_connection_success(
    qtbot: QtBot,
    main_window: MainWindow,
):
    """
    Verifica que se actualiza correctamente una conexión Oracle válida.
    """

    form, connection = _open_connection_form(
        qtbot,
        main_window,
        "1 - E2E Oracle",
    )

    assert form.name_input.text() == connection.name
    assert form.driver_input.currentText() == connection.driver.value
    assert form.host_input.text() == connection.host
    assert form.port_input.text() == str(connection.port)
    assert form.database_input.text() == connection.database
    assert form.username_input.text() == connection.username
    assert form.password_input.text() == connection.password

    form.name_input.setText("Updated Oracle connection")
    form.host_input.setText("127.0.0.1")
    form.port_input.setText("1522")
    form.database_input.setText("updated-oracle")
    form.username_input.setText("updated-user")
    form.password_input.setText("updated-password")

    form.save_button.click()

    connections = get_all_connections()

    assert len(connections) == _INITIAL_CONNECTIONS

    updated_connection = next(
        connection for connection in connections if connection.id == "1-e2e-oracle"
    )

    assert updated_connection.name == "Updated Oracle connection"
    assert updated_connection.driver == Driver.ORACLE
    assert updated_connection.host == "127.0.0.1"
    assert updated_connection.port == 1522
    assert updated_connection.database == "updated-oracle"
    assert updated_connection.username == "updated-user"
    assert updated_connection.password == "updated-password"

    assert main_window.stack.currentWidget() is main_window.home_page

    assert (
        main_window.sidebar.connections_list.list_widget.count() == _INITIAL_CONNECTIONS
    )


def test_update_oracle_connection_invalid_data(
    qtbot: QtBot,
    main_window: MainWindow,
):
    """
    Verifica que no se actualiza una conexión Oracle con datos inválidos.
    """

    form, connection = _open_connection_form(
        qtbot,
        main_window,
        "1 - E2E Oracle",
    )

    assert form.name_input.text() == connection.name
    assert form.driver_input.currentText() == connection.driver.value
    assert form.host_input.text() == connection.host
    assert form.port_input.text() == str(connection.port)
    assert form.database_input.text() == connection.database
    assert form.username_input.text() == connection.username
    assert form.password_input.text() == connection.password

    form.name_input.clear()
    form.host_input.clear()
    form.port_input.clear()
    form.database_input.clear()
    form.username_input.clear()
    form.password_input.clear()

    form.save_button.click()

    assert len(get_all_connections()) == _INITIAL_CONNECTIONS

    persisted_connection = next(
        connection
        for connection in get_all_connections()
        if connection.id == "1-e2e-oracle"
    )

    assert persisted_connection == connection

    assert main_window.stack.currentWidget() is main_window.connection_form_page

    assert (
        main_window.sidebar.connections_list.list_widget.count() == _INITIAL_CONNECTIONS
    )

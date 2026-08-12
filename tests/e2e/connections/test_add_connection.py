from PySide6.QtWidgets import QPushButton
from pytestqt.qtbot import QtBot

from entities.driver import Driver
from modules.connections.model import get_all_connections
from ui.app.main_window import MainWindow

# =============================================================================
# VARIABLES
# =============================================================================

_INITIAL_CONNECTIONS = 4
_NEW_CONNECTION_POSITION = 4

# =============================================================================
# FUNCTIONS
# =============================================================================


def _open_connection_form(
    qtbot: QtBot,
    window: MainWindow,
):
    """
    Abre el formulario de creación de una nueva conexión.

    Localiza el botón de añadir conexión en la ventana principal,
    simula un clic sobre él y verifica que la aplicación navega
    correctamente hasta el formulario de conexiones.

    Args:
        qtbot (QtBot):
            Fixture de pytest-qt utilizada para interactuar con
            la interfaz gráfica durante los tests.

        window (MainWindow):
            Ventana principal de la aplicación sobre la que se
            realizará la interacción.

    Returns:
        ConnectionForm:
            Formulario de conexión actualmente mostrado.
    """

    add_button = window.findChild(
        QPushButton,
        "add_connection",
    )

    assert add_button is not None

    add_button.click()

    assert window.stack.currentWidget() is window.connection_form_page

    return window.connection_form


# =============================================================================
# TESTS
# =============================================================================


def test_create_sqlite_connection_success(
    qtbot: QtBot,
    main_window: MainWindow,
):
    """
    Verifica que se crea correctamente una conexión SQLite válida.
    """

    form = _open_connection_form(
        qtbot,
        main_window,
    )

    form.name_input.setText("SQLite connection")
    form.driver_input.setCurrentText(Driver.SQLITE.value)
    form.path_input.setText("/tmp/database.db")

    form.save_button.click()

    connections = get_all_connections()

    assert len(connections) == _INITIAL_CONNECTIONS + 1

    connection = connections[_NEW_CONNECTION_POSITION]

    assert connection.name == "SQLite connection"
    assert connection.driver == Driver.SQLITE
    assert connection.path == "/tmp/database.db"

    assert main_window.stack.currentWidget() is main_window.home_page

    assert (
        main_window.sidebar.connections_list.list_widget.count()
        == _INITIAL_CONNECTIONS + 1
    )


def test_create_sqlite_connection_invalid_data(
    qtbot: QtBot,
    main_window: MainWindow,
):
    """
    Verifica que no se crea una conexión SQLite con datos inválidos.
    """

    form = _open_connection_form(
        qtbot,
        main_window,
    )

    form.driver_input.setCurrentText(Driver.SQLITE.value)

    # Nombre y ruta vacíos.

    form.save_button.click()

    assert len(get_all_connections()) == _INITIAL_CONNECTIONS

    assert main_window.stack.currentWidget() is main_window.connection_form_page

    assert (
        main_window.sidebar.connections_list.list_widget.count() == _INITIAL_CONNECTIONS
    )


def test_create_postgresql_connection_success(
    qtbot: QtBot,
    main_window: MainWindow,
):
    """
    Verifica que se crea correctamente una conexión PostgreSQL válida.
    """

    form = _open_connection_form(
        qtbot,
        main_window,
    )

    form.name_input.setText("PostgreSQL connection")
    form.driver_input.setCurrentText(Driver.POSTGRESQL.value)
    form.host_input.setText("localhost")
    form.port_input.setText("5432")
    form.database_input.setText("postgres")
    form.username_input.setText("postgres")
    form.password_input.setText("postgres")

    form.save_button.click()

    connections = get_all_connections()

    assert len(connections) == _INITIAL_CONNECTIONS + 1

    connection = connections[_NEW_CONNECTION_POSITION]

    assert connection.name == "PostgreSQL connection"
    assert connection.driver == Driver.POSTGRESQL
    assert connection.host == "localhost"
    assert connection.port == 5432
    assert connection.database == "postgres"
    assert connection.username == "postgres"
    assert connection.password == "postgres"

    assert main_window.stack.currentWidget() is main_window.home_page

    assert (
        main_window.sidebar.connections_list.list_widget.count()
        == _INITIAL_CONNECTIONS + 1
    )


def test_create_postgresql_connection_invalid_data(
    qtbot: QtBot,
    main_window: MainWindow,
):
    """
    Verifica que no se crea una conexión PostgreSQL con datos inválidos.
    """

    form = _open_connection_form(
        qtbot,
        main_window,
    )

    form.name_input.setText("Broken connection")
    form.driver_input.setCurrentText(Driver.POSTGRESQL.value)

    # Dejamos todos los campos obligatorios vacíos.

    form.save_button.click()

    assert len(get_all_connections()) == _INITIAL_CONNECTIONS

    assert main_window.stack.currentWidget() is main_window.connection_form_page

    assert (
        main_window.sidebar.connections_list.list_widget.count() == _INITIAL_CONNECTIONS
    )


def test_create_mysql_connection_success(
    qtbot: QtBot,
    main_window: MainWindow,
):
    """
    Verifica que se crea correctamente una conexión MySQL válida.
    """

    form = _open_connection_form(
        qtbot,
        main_window,
    )

    form.name_input.setText("MySQL connection")
    form.driver_input.setCurrentText(
        Driver.MYSQL.value,
    )
    form.host_input.setText("localhost")
    form.port_input.setText("3306")
    form.database_input.setText("mysql")
    form.username_input.setText("mysql")
    form.password_input.setText("mysql")

    form.save_button.click()

    connections = get_all_connections()

    assert len(connections) == _INITIAL_CONNECTIONS + 1

    connection = connections[_NEW_CONNECTION_POSITION]

    assert connection.name == "MySQL connection"
    assert connection.driver == Driver.MYSQL
    assert connection.host == "localhost"
    assert connection.port == 3306
    assert connection.database == "mysql"
    assert connection.username == "mysql"
    assert connection.password == "mysql"

    assert main_window.stack.currentWidget() is main_window.home_page

    assert (
        main_window.sidebar.connections_list.list_widget.count()
        == _INITIAL_CONNECTIONS + 1
    )


def test_create_mysql_connection_invalid_data(
    qtbot: QtBot,
    main_window: MainWindow,
):
    """
    Verifica que no se crea una conexión MySQL con datos inválidos.
    """

    form = _open_connection_form(
        qtbot,
        main_window,
    )

    form.name_input.setText("Broken connection")
    form.driver_input.setCurrentText(Driver.MYSQL.value)

    # Dejamos todos los campos obligatorios vacíos.

    form.save_button.click()

    assert len(get_all_connections()) == _INITIAL_CONNECTIONS

    assert main_window.stack.currentWidget() is main_window.connection_form_page

    assert (
        main_window.sidebar.connections_list.list_widget.count() == _INITIAL_CONNECTIONS
    )


def test_create_oracle_connection_success(
    qtbot: QtBot,
    main_window: MainWindow,
):
    """
    Verifica que se crea correctamente una conexión Oracle válida.
    """

    form = _open_connection_form(
        qtbot,
        main_window,
    )

    form.name_input.setText("Oracle connection")
    form.driver_input.setCurrentText(Driver.ORACLE.value)
    form.host_input.setText("localhost")
    form.port_input.setText("1521")
    form.database_input.setText("oracle")
    form.username_input.setText("oracle")
    form.password_input.setText("oracle")

    form.save_button.click()

    connections = get_all_connections()

    assert len(connections) == _INITIAL_CONNECTIONS + 1

    connection = connections[_NEW_CONNECTION_POSITION]

    assert connection.name == "Oracle connection"
    assert connection.driver == Driver.ORACLE
    assert connection.host == "localhost"
    assert connection.port == 1521
    assert connection.database == "oracle"
    assert connection.username == "oracle"
    assert connection.password == "oracle"

    assert main_window.stack.currentWidget() is main_window.home_page

    assert (
        main_window.sidebar.connections_list.list_widget.count()
        == _INITIAL_CONNECTIONS + 1
    )


def test_create_oracle_connection_invalid_data(
    qtbot: QtBot,
    main_window: MainWindow,
):
    """
    Verifica que no se crea una conexión Oracle con datos inválidos.
    """

    form = _open_connection_form(
        qtbot,
        main_window,
    )

    form.name_input.setText("Broken connection")
    form.driver_input.setCurrentText(Driver.ORACLE.value)

    # Dejamos todos los campos obligatorios vacíos.

    form.save_button.click()

    assert len(get_all_connections()) == _INITIAL_CONNECTIONS

    assert main_window.stack.currentWidget() is main_window.connection_form_page

    assert (
        main_window.sidebar.connections_list.list_widget.count() == _INITIAL_CONNECTIONS
    )

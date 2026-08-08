from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton
from pytestqt.qtbot import QtBot

from entities.driver import Driver
from modules.connections.model import get_all_connections
from ui.app.main_window import MainWindow


def _open_connection_form(
    qtbot: QtBot,
    window: MainWindow,
):
    add_button = window.findChild(
        QPushButton,
        "add_connection",
    )

    assert add_button is not None

    qtbot.mouseClick(
        add_button,
        Qt.MouseButton.LeftButton,
    )

    assert window.stack.currentWidget() is window.connection_form_page

    return window.connection_form


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

    qtbot.keyClicks(
        form.name_input,
        "SQLite connection",
    )

    form.driver_input.setCurrentText(
        Driver.SQLITE.value,
    )

    qtbot.keyClicks(
        form.path_input,
        "/tmp/database.db",
    )

    qtbot.mouseClick(
        form.save_button,
        Qt.MouseButton.LeftButton,
    )

    connections = get_all_connections()

    assert len(connections) == 1

    connection = connections[0]

    assert connection.name == "SQLite connection"
    assert connection.driver == Driver.SQLITE
    assert connection.path == "/tmp/database.db"

    assert main_window.stack.currentWidget() is main_window.home_page

    assert main_window.sidebar.connections_list.list_widget.count() == 1


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

    form.driver_input.setCurrentText(
        Driver.SQLITE.value,
    )

    # Nombre y ruta vacíos.

    qtbot.mouseClick(
        form.save_button,
        Qt.MouseButton.LeftButton,
    )

    assert get_all_connections() == []

    assert main_window.stack.currentWidget() is main_window.connection_form_page

    assert main_window.sidebar.connections_list.list_widget.count() == 0


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

    assert len(connections) == 1

    connection = connections[0]

    assert connection.name == "PostgreSQL connection"
    assert connection.driver == Driver.POSTGRESQL
    assert connection.host == "localhost"
    assert connection.port == 5432
    assert connection.database == "postgres"
    assert connection.username == "postgres"
    assert connection.password == "postgres"

    assert main_window.stack.currentWidget() is main_window.home_page

    assert main_window.sidebar.connections_list.list_widget.count() == 1


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

    qtbot.keyClicks(
        form.name_input,
        "Broken connection",
    )

    form.driver_input.setCurrentText(
        Driver.POSTGRESQL.value,
    )

    # Dejamos todos los campos obligatorios vacíos.

    qtbot.mouseClick(
        form.save_button,
        Qt.MouseButton.LeftButton,
    )

    assert get_all_connections() == []

    assert main_window.stack.currentWidget() is main_window.connection_form_page

    assert main_window.sidebar.connections_list.list_widget.count() == 0


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

    assert len(connections) == 1

    connection = connections[0]

    assert connection.name == "MySQL connection"
    assert connection.driver == Driver.MYSQL
    assert connection.host == "localhost"
    assert connection.port == 3306
    assert connection.database == "mysql"
    assert connection.username == "mysql"
    assert connection.password == "mysql"

    assert main_window.stack.currentWidget() is main_window.home_page

    assert main_window.sidebar.connections_list.list_widget.count() == 1


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

    form.name_input.setText(
        "Broken connection",
    )

    form.driver_input.setCurrentText(
        Driver.MYSQL.value,
    )

    # Dejamos todos los campos obligatorios vacíos.

    form.save_button.click()

    assert get_all_connections() == []

    assert main_window.stack.currentWidget() is main_window.connection_form_page

    assert main_window.sidebar.connections_list.list_widget.count() == 0


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

    form.name_input.setText(
        "Oracle connection",
    )

    form.driver_input.setCurrentText(
        Driver.ORACLE.value,
    )

    form.host_input.setText(
        "localhost",
    )

    form.port_input.setText(
        "1521",
    )

    form.database_input.setText(
        "oracle",
    )

    form.username_input.setText(
        "oracle",
    )

    form.password_input.setText(
        "oracle",
    )

    form.save_button.click()

    connections = get_all_connections()

    assert len(connections) == 1

    connection = connections[0]

    assert connection.name == "Oracle connection"
    assert connection.driver == Driver.ORACLE
    assert connection.host == "localhost"
    assert connection.port == 1521
    assert connection.database == "oracle"
    assert connection.username == "oracle"
    assert connection.password == "oracle"

    assert main_window.stack.currentWidget() is main_window.home_page

    assert main_window.sidebar.connections_list.list_widget.count() == 1


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

    form.name_input.setText(
        "Broken connection",
    )

    form.driver_input.setCurrentText(
        Driver.ORACLE.value,
    )

    # Dejamos todos los campos obligatorios vacíos.

    form.save_button.click()

    assert get_all_connections() == []

    assert main_window.stack.currentWidget() is main_window.connection_form_page

    assert main_window.sidebar.connections_list.list_widget.count() == 0

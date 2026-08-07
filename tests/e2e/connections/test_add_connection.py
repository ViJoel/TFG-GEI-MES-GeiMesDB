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

    qtbot.keyClicks(
        form.name_input,
        "PostgreSQL connection",
    )

    form.driver_input.setCurrentText(
        Driver.POSTGRESQL.value,
    )

    qtbot.keyClicks(
        form.host_input,
        "localhost",
    )

    form.port_input.setFocus()
    qtbot.keyClicks(
        form.port_input,
        "5432",
    )

    qtbot.keyClicks(
        form.database_input,
        "postgres",
    )

    qtbot.keyClicks(
        form.username_input,
        "postgres",
    )

    qtbot.keyClicks(
        form.password_input,
        "postgres",
    )

    qtbot.mouseClick(
        form.save_button,
        Qt.MouseButton.LeftButton,
    )

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

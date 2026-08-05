from unittest.mock import MagicMock

import pytest

import ui.widgets.forms.connection_form as connection_form
from entities.connection import Connection
from entities.driver import Driver
from entities.message_type import MessageType
from ui.app.worker_error import WorkerError
from ui.widgets.forms.connection_form import ConnectionForm

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def form(qtbot):
    form = ConnectionForm()

    qtbot.addWidget(form)
    form.show()

    return form


@pytest.fixture
def connection():
    """
    Construye una conexión de prueba.
    """

    return Connection(
        id="1",
        name="Test",
        driver=Driver.POSTGRESQL,
        host="localhost",
        port=5432,
        database="postgres",
        username="admin",
        password="secret",
    )


# =============================================================================
# INITIALIZATION
# =============================================================================


def test_form_is_created(form):
    """
    Verifica que el formulario se crea correctamente.
    """

    assert form.objectName() == "connection_form"
    assert form.isVisible()
    assert form.current_connection is None


def test_form_is_empty_on_creation(form):
    """
    Verifica que el formulario se inicializa vacío.
    """

    assert form.name_input.text() == ""
    assert form.host_input.text() == ""
    assert form.port_input.text() == ""
    assert form.database_input.text() == ""
    assert form.username_input.text() == ""
    assert form.password_input.text() == ""
    assert form.path_input.text() == ""


def test_default_driver_is_first_enum_value(form):
    """
    Verifica que SQLite es el driver seleccionado por defecto.
    """

    assert form.driver_input.currentText() == Driver.SQLITE.value


# =============================================================================
# UI STATE
# =============================================================================


def test_sqlite_driver_shows_only_sqlite_fields(form):
    """
    Verifica que SQLite muestra únicamente los campos correspondientes.
    """

    form.driver_input.setCurrentText(Driver.SQLITE.value)

    assert form.path_field.isVisible()

    assert not form.host_field.isVisible()
    assert not form.port_field.isVisible()
    assert not form.database_field.isVisible()
    assert not form.username_field.isVisible()
    assert not form.password_field.isVisible()


def test_network_driver_shows_network_fields(form):
    """
    Verifica que los drivers de red muestran los campos correspondientes.
    """

    for driver in Driver:

        if driver == Driver.SQLITE:
            continue

        form.driver_input.setCurrentText(driver.value)

        assert form.host_field.isVisible()
        assert form.port_field.isVisible()
        assert form.database_field.isVisible()
        assert form.username_field.isVisible()
        assert form.password_field.isVisible()
        assert not form.path_field.isVisible()


# =============================================================================
# EVENT HANDLERS
# =============================================================================


def test_clear_form_clears_all_fields(form):
    """
    Verifica que el formulario limpia todos los campos.
    """

    form.name_input.setText("Personal DB")
    form.host_input.setText("localhost")
    form.port_input.setText("5432")
    form.database_input.setText("postgres")
    form.username_input.setText("postgres")
    form.password_input.setText("secret")
    form.path_input.setText("/tmp/database.db")

    form.clear_form()

    assert form.name_input.text() == ""
    assert form.host_input.text() == ""
    assert form.port_input.text() == ""
    assert form.database_input.text() == ""
    assert form.username_input.text() == ""
    assert form.password_input.text() == ""
    assert form.path_input.text() == ""


def test_clear_form_removes_current_connection(form):
    """
    Verifica que el formulario elimina la conexión cargada.
    """

    form.current_connection = Connection()
    form.clear_form()

    assert form.current_connection is None


def test_clear_form_restores_default_driver(form):
    """
    Verifica que el formulario restaura el driver por defecto.
    """

    form.driver_input.setCurrentText(Driver.POSTGRESQL.value)
    form.clear_form()

    assert form.driver_input.currentText() == Driver.SQLITE.value


def test_clear_form_restores_default_visibility(form):
    """
    Verifica que el formulario restaura la visibilidad inicial de los campos.
    """

    form.driver_input.setCurrentText(Driver.POSTGRESQL.value)
    form.clear_form()

    assert form.path_field.isVisible()

    assert not form.host_field.isVisible()
    assert not form.port_field.isVisible()
    assert not form.database_field.isVisible()
    assert not form.username_field.isVisible()
    assert not form.password_field.isVisible()


# =============================================================================
# LOAD CONNECTION
# =============================================================================


def test_load_network_connection_populates_fields(form, connection):
    """
    Verifica que el formulario carga una conexión de red.
    """

    form.load_connection(connection)

    assert form.current_connection is connection

    assert form.name_input.text() == "Test"
    assert form.driver_input.currentText() == Driver.POSTGRESQL.value
    assert form.host_input.text() == "localhost"
    assert form.port_input.text() == "5432"
    assert form.database_input.text() == "postgres"
    assert form.username_input.text() == "admin"
    assert form.password_input.text() == "secret"


def test_load_sqlite_connection_populates_fields(form):
    """
    Verifica que el formulario carga una conexión SQLite.
    """

    connection = Connection()

    connection.name = "SQLite"
    connection.driver = Driver.SQLITE
    connection.path = "/tmp/database.db"

    form.load_connection(connection)

    assert form.current_connection is connection

    assert form.name_input.text() == "SQLite"
    assert form.driver_input.currentText() == Driver.SQLITE.value
    assert form.path_input.text() == "/tmp/database.db"


# =============================================================================
# BUILD CONNECTION
# =============================================================================


def test_build_network_connection(form):
    """
    Verifica que el formulario construye una conexión de red.
    """

    form.name_input.setText("Producción")
    form.driver_input.setCurrentText(Driver.POSTGRESQL.value)
    form.host_input.setText("localhost")
    form.port_input.setText("5432")
    form.database_input.setText("postgres")
    form.username_input.setText("admin")
    form.password_input.setText("secret")

    connection = form._build_connection_from_form()

    assert connection.name == "Producción"
    assert connection.driver == Driver.POSTGRESQL
    assert connection.host == "localhost"
    assert connection.port == 5432
    assert connection.database == "postgres"
    assert connection.username == "admin"
    assert connection.password == "secret"

    assert connection.path is None


def test_build_sqlite_connection(form):
    """
    Verifica que el formulario construye una conexión SQLite.
    """

    form.name_input.setText("SQLite")
    form.driver_input.setCurrentText(Driver.SQLITE.value)
    form.path_input.setText("/tmp/database.db")

    connection = form._build_connection_from_form()

    assert connection.name == "SQLite"
    assert connection.driver == Driver.SQLITE
    assert connection.path == "/tmp/database.db"

    assert connection.host is None
    assert connection.port is None
    assert connection.database is None
    assert connection.username is None
    assert connection.password is None


def test_build_connection_reuses_loaded_connection(form, connection):
    """
    Verifica que el formulario reutiliza la conexión cargada.
    """

    form.current_connection = connection

    result = form._build_connection_from_form()

    assert result is connection


# =============================================================================
# SAVE CONNECTION
# =============================================================================


def test_save_button_creates_connection(form, connection, monkeypatch):
    """
    Verifica que el formulario crea una nueva conexión.
    """

    create_connection = MagicMock()
    notify = MagicMock()

    monkeypatch.setattr(
        connection_form,
        "create_connection",
        create_connection,
    )

    monkeypatch.setattr(
        connection_form,
        "notify",
        notify,
    )

    form.name_input.setText(connection.name)
    form.driver_input.setCurrentText(connection.driver.value)
    form.host_input.setText(connection.host)
    form.port_input.setText(str(connection.port))
    form.database_input.setText(connection.database)
    form.username_input.setText(connection.username)
    form.password_input.setText(connection.password)

    form.save_button.click()

    create_connection.assert_called_once()


def test_save_button_updates_connection(form, connection, monkeypatch):
    """
    Verifica que el formulario actualiza una conexión existente.
    """

    update_connection = MagicMock()
    notify = MagicMock()

    monkeypatch.setattr(
        connection_form,
        "update_connection",
        update_connection,
    )

    monkeypatch.setattr(
        connection_form,
        "notify",
        notify,
    )

    form.load_connection(connection)

    form.save_button.click()

    update_connection.assert_called_once_with(connection)


def test_save_button_emits_connection_saved_signal(
    form,
    connection,
    qtbot,
    monkeypatch,
):
    """
    Verifica que el formulario emite la señal de conexión guardada.
    """

    monkeypatch.setattr(
        connection_form,
        "create_connection",
        MagicMock(),
    )

    monkeypatch.setattr(
        connection_form,
        "notify",
        MagicMock(),
    )

    form.name_input.setText(connection.name)
    form.driver_input.setCurrentText(connection.driver.value)
    form.host_input.setText(connection.host)
    form.port_input.setText(str(connection.port))
    form.database_input.setText(connection.database)
    form.username_input.setText(connection.username)
    form.password_input.setText(connection.password)

    with qtbot.waitSignal(form.connection_saved):
        form.save_button.click()


def test_save_button_handles_create_exception(
    form,
    connection,
    monkeypatch,
):
    """
    Verifica que un error al crear la conexión
    muestra la notificación correspondiente.
    """

    create_connection = MagicMock(side_effect=RuntimeError("boom"))
    notify = MagicMock()
    saved = MagicMock()

    monkeypatch.setattr(
        connection_form,
        "create_connection",
        create_connection,
    )

    monkeypatch.setattr(
        connection_form,
        "notify",
        notify,
    )

    form.connection_saved.connect(saved)

    form.name_input.setText(connection.name)
    form.driver_input.setCurrentText(connection.driver.value)
    form.host_input.setText(connection.host)
    form.port_input.setText(str(connection.port))
    form.database_input.setText(connection.database)
    form.username_input.setText(connection.username)
    form.password_input.setText(connection.password)

    form.save_button.click()

    create_connection.assert_called_once()

    notify.assert_called_once_with(
        MessageType.ERROR,
        form.tr("Error saving."),
    )

    saved.assert_not_called()


def test_save_button_handles_update_exception(
    form,
    connection,
    monkeypatch,
):
    """
    Verifica que un error al actualizar la conexión
    muestra la notificación correspondiente.
    """

    update_connection = MagicMock(side_effect=RuntimeError("boom"))
    notify = MagicMock()
    saved = MagicMock()

    monkeypatch.setattr(
        connection_form,
        "update_connection",
        update_connection,
    )

    monkeypatch.setattr(
        connection_form,
        "notify",
        notify,
    )

    form.connection_saved.connect(saved)

    form.load_connection(connection)

    form.save_button.click()

    update_connection.assert_called_once()

    notify.assert_called_once_with(
        MessageType.ERROR,
        form.tr("Error saving."),
    )

    saved.assert_not_called()


# =============================================================================
# TEST CONNECTION
# =============================================================================


def test_test_connection_starts_background_task(
    form,
    connection,
    monkeypatch,
):
    """
    Verifica que el formulario lanza la prueba de
    conexión mediante el TaskManager.
    """

    notify = MagicMock()

    task_manager = MagicMock()

    monkeypatch.setattr(
        connection_form,
        "notify",
        notify,
    )

    monkeypatch.setattr(
        connection_form.AppContext,
        "get_task_manager",
        MagicMock(return_value=task_manager),
    )

    form.name_input.setText(connection.name)
    form.driver_input.setCurrentText(connection.driver.value)
    form.host_input.setText(connection.host)
    form.port_input.setText(str(connection.port))
    form.database_input.setText(connection.database)
    form.username_input.setText(connection.username)
    form.password_input.setText(connection.password)

    form.test_connection_button.click()

    notify.assert_called_once()

    task_manager.run.assert_called_once()

    args = task_manager.run.call_args.args
    kwargs = task_manager.run.call_args.kwargs

    assert args[0] is connection_form.test_connection
    assert isinstance(args[1], Connection)

    assert callable(kwargs["on_success"])
    assert kwargs["on_error"] == form._on_test_connection_error


def test_on_test_connection_success(form, monkeypatch):
    """
    Debe mostrar una notificación de éxito.
    """

    notify = MagicMock()

    monkeypatch.setattr(
        connection_form,
        "notify",
        notify,
    )

    form._on_test_connection_success(True)

    notify.assert_called_once_with(
        MessageType.SUCCESS,
        form.tr("Connection successful."),
    )


def test_on_test_connection_failure(form, monkeypatch):
    """
    Debe mostrar una notificación de error.
    """

    notify = MagicMock()

    monkeypatch.setattr(
        connection_form,
        "notify",
        notify,
    )

    form._on_test_connection_success(False)

    notify.assert_called_once_with(
        MessageType.ERROR,
        form.tr("Connection failed."),
    )


def test_on_test_connection_error(form, monkeypatch):
    """
    Debe notificar un error cuando el Worker falla.
    """

    notify = MagicMock()

    monkeypatch.setattr(
        connection_form,
        "notify",
        notify,
    )

    error = WorkerError(
        exception=RuntimeError("boom"),
        traceback="traceback",
    )

    form._on_test_connection_error(error)

    notify.assert_called_once_with(
        MessageType.ERROR,
        form.tr("Invalid connection data."),
    )


# =============================================================================
# FILE SELECTION
# =============================================================================


def test_select_file_updates_path(form, monkeypatch):
    """
    Verifica que el formulario carga la ruta del archivo seleccionado.
    """

    monkeypatch.setattr(
        connection_form.QFileDialog,
        "getOpenFileName",
        MagicMock(return_value=("/tmp/database.db", "")),
    )

    form._select_file()

    assert form.path_input.text() == "/tmp/database.db"


def test_select_file_keeps_path_when_dialog_is_cancelled(
    form,
    monkeypatch,
):
    """
    Verifica que el formulario mantiene la ruta cuando se cancela el diálogo.
    """

    form.path_input.setText("/tmp/database.db")

    monkeypatch.setattr(
        connection_form.QFileDialog,
        "getOpenFileName",
        MagicMock(return_value=("", "")),
    )

    form._select_file()

    assert form.path_input.text() == "/tmp/database.db"


# =============================================================================
# CANCEL
# =============================================================================


def test_cancel_button_clears_form(form):
    """
    Verifica que cancelar limpia el formulario.
    """

    form.name_input.setText("Test")
    form.host_input.setText("localhost")
    form.port_input.setText("5432")
    form.database_input.setText("postgres")
    form.username_input.setText("admin")
    form.password_input.setText("secret")
    form.path_input.setText("/tmp/database.db")

    form.cancel_button.click()

    assert form.name_input.text() == ""
    assert form.host_input.text() == ""
    assert form.port_input.text() == ""
    assert form.database_input.text() == ""
    assert form.username_input.text() == ""
    assert form.password_input.text() == ""
    assert form.path_input.text() == ""


def test_cancel_button_emits_signal(form, qtbot):
    """
    Verifica que cancelar emite la señal correspondiente.
    """

    with qtbot.waitSignal(form.cancel_requested):
        form.cancel_button.click()


# =============================================================================
# INTERNATIONALIZATION
# =============================================================================


def test_retranslate_ui_updates_all_translatable_texts(form):
    """
    Verifica que la interfaz actualiza correctamente todos
    los textos traducibles del formulario.
    """

    form._retranslate_ui()

    # Título.

    assert form.title_label.text() == form.tr("Connection form")

    # Labels.

    assert form._name_field_label.text() == form.tr("Name")
    assert form._driver_field_label.text() == form.tr("Driver")
    assert form._host_field_label.text() == form.tr("Host")
    assert form._port_field_label.text() == form.tr("Port")
    assert form._database_field_label.text() == form.tr("Database")
    assert form._username_field_label.text() == form.tr("Username")
    assert form._password_field_label.text() == form.tr("Password")
    assert form.path_input_label.text() == form.tr("Path to the file")

    # Placeholders.

    assert form.name_input.placeholderText() == form.tr("My personal DB")
    assert form.path_input.placeholderText() == form.tr("/path/to/the/file.db")

    # Botón de selección de archivo.

    assert form.browse_button.text() == form.tr("Browse")

    # Botones de acción.

    assert form.test_connection_button.text() == form.tr("Test connection")
    assert form.cancel_button.text() == form.tr("Cancel")
    assert form.save_button.text() == form.tr("Save")

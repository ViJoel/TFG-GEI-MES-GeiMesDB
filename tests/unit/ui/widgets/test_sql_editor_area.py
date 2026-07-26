from pathlib import Path
from unittest.mock import MagicMock

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QShortcut
from PySide6.QtWidgets import (
    QSplitter,
    QStackedWidget,
)

from entities.sql_scope import SqlScope
from ui.widgets.workspace.sql_editor.sql_editor_area import SqlEditorArea

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def sql_editor_area(qtbot):
    """
    Instancia real del widget.
    """

    widget = SqlEditorArea()
    qtbot.addWidget(widget)
    return widget


@pytest.fixture
def fake_file(mocker):
    """
    File falso reutilizable.
    """

    file = mocker.Mock()

    file.name = "query.sql"
    file.path = Path("/tmp/query.sql")
    file.has_changes = False
    file.existsOnDisk = True

    return file


@pytest.fixture
def fake_editor(fake_file, mocker):
    """
    Editor falso reutilizable.
    """

    editor = mocker.Mock()

    editor.file = fake_file

    return editor


@pytest.fixture
def notify_mock(mocker):
    return mocker.patch("ui.widgets.workspace.sql_editor.sql_editor_area.notify")


@pytest.fixture
def open_file_mock(mocker):
    return mocker.patch(
        "ui.widgets.workspace.sql_editor.sql_editor_area.files_service.open_file"
    )


@pytest.fixture
def save_file_mock(mocker):
    return mocker.patch(
        "ui.widgets.workspace.sql_editor.sql_editor_area.files_service.save_file"
    )


@pytest.fixture
def rename_dialog_mock(mocker):
    return mocker.patch(
        "ui.widgets.workspace.sql_editor.sql_editor_area.RenameFileDialog.get_new_name"
    )


@pytest.fixture
def confirmation_dialog_mock(mocker):
    dialog = mocker.Mock()
    dialog.exec.return_value = True

    mocker.patch(
        "ui.widgets.workspace.sql_editor.sql_editor_area.ConfirmationDialog",
        return_value=dialog,
    )

    return dialog


@pytest.fixture
def open_dialog_mock(mocker):
    return mocker.patch(
        "ui.widgets.workspace.sql_editor.sql_editor_area.QFileDialog.getOpenFileName"
    )


@pytest.fixture
def save_dialog_mock(mocker):
    return mocker.patch(
        "ui.widgets.workspace.sql_editor.sql_editor_area.QFileDialog.getSaveFileName"
    )


# =============================================================================
# INICIALIZACIÓN
# =============================================================================


def test_initialization(sql_editor_area):
    """
    Comprueba la creación del widget.
    """

    assert sql_editor_area.objectName() == "sql_editor_area"
    assert sql_editor_area.files == []


def test_ui_created(sql_editor_area):
    """
    Comprueba la creación de la UI.
    """

    assert isinstance(sql_editor_area.splitter, QSplitter)
    assert isinstance(sql_editor_area.editors, QStackedWidget)

    assert hasattr(sql_editor_area, "toolbar")
    assert hasattr(sql_editor_area, "files_list")


def test_splitter_configuration(sql_editor_area):
    """
    Comprueba la configuración del splitter.
    """

    splitter = sql_editor_area.splitter

    assert splitter.orientation() == Qt.Horizontal
    assert splitter.handleWidth() == 1
    assert splitter.childrenCollapsible() is True
    assert splitter.count() == 2


# =============================================================================
# SEÑALES
# =============================================================================


def test_execute_requested_signal(sql_editor_area, qtbot):
    """
    Comprueba la emisión de la señal principal.
    """

    files = []
    obj = object()

    with qtbot.waitSignal(sql_editor_area.execute_requested) as blocker:
        sql_editor_area.execute_requested.emit(
            files,
            obj,
        )

    assert blocker.args == [files, obj]


# =============================================================================
# SHORTCUTS
# =============================================================================


def test_shortcuts_exist(sql_editor_area):
    """
    Comprueba que existen todos los shortcuts.
    """

    shortcuts = {
        shortcut.key().toString(): shortcut
        for shortcut in sql_editor_area.findChildren(QShortcut)
    }

    assert set(shortcuts.keys()) == {
        "Ctrl+N",
        "Ctrl+O",
        "Ctrl+W",
    }


@pytest.mark.parametrize(
    ("shortcut", "handler"),
    [
        ("Ctrl+N", "_on_new_file_requested"),
        ("Ctrl+O", "_on_open_file_requested"),
        ("Ctrl+W", "_on_close_current_file_requested"),
    ],
)
def test_shortcuts_trigger_handlers(
    sql_editor_area,
    mocker,
    shortcut,
    handler,
):
    """
    Comprueba que cada shortcut invoca su handler correspondiente.
    """

    handler_mock = mocker.patch.object(
        sql_editor_area,
        handler,
    )

    shortcuts = {s.key().toString(): s for s in sql_editor_area.findChildren(QShortcut)}

    shortcut_obj = shortcuts[shortcut]

    # El shortcut quedó conectado al método original durante __init__,
    # por lo que es necesario sustituir dicha conexión por el mock.
    shortcut_obj.activated.disconnect()
    shortcut_obj.activated.connect(handler_mock)

    shortcut_obj.activated.emit()

    handler_mock.assert_called_once_with()


# =============================================================================
# MÉTODOS QUE DEPENDEN DEL EDITOR ACTUAL
# =============================================================================


@pytest.mark.parametrize(
    (
        "method",
        "editor_method",
        "expected_arg",
    ),
    [
        (
            "_undo_current",
            "undo",
            None,
        ),
        (
            "_redo_current",
            "redo",
            None,
        ),
        (
            "_execute_selection",
            "execute",
            SqlScope.SELECTED_TEXT,
        ),
        (
            "_execute_query",
            "execute",
            SqlScope.ACTUAL_QUERY,
        ),
        (
            "_execute_script",
            "execute",
            SqlScope.FULL_SCRIPT,
        ),
    ],
)
def test_editor_actions_call_editor(
    sql_editor_area,
    fake_editor,
    mocker,
    method,
    editor_method,
    expected_arg,
):
    """
    Comprueba que los métodos delegan en el editor activo.
    """

    mocker.patch.object(
        sql_editor_area,
        "_get_current_editor",
        return_value=fake_editor,
    )

    getattr(sql_editor_area, method)()

    editor_call = getattr(
        fake_editor,
        editor_method,
    )

    if expected_arg is None:
        editor_call.assert_called_once_with()
    else:
        editor_call.assert_called_once_with(expected_arg)


@pytest.mark.parametrize(
    "method",
    [
        "_undo_current",
        "_redo_current",
        "_execute_selection",
        "_execute_query",
        "_execute_script",
    ],
)
def test_editor_actions_without_editor(
    sql_editor_area,
    mocker,
    method,
):
    """
    Comprueba que no ocurre nada cuando no existe editor activo.
    """

    mocker.patch.object(
        sql_editor_area,
        "_get_current_editor",
        return_value=None,
    )

    getattr(sql_editor_area, method)()


# =============================================================================
# NUEVO ARCHIVO
# =============================================================================


def test_on_new_file_requested_creates_file(
    sql_editor_area,
    mocker,
):
    """
    Debe crear un File nuevo y delegar en _add_file_and_editor().
    """

    add_mock = mocker.patch.object(
        sql_editor_area,
        "_add_file_and_editor",
    )

    sql_editor_area._on_new_file_requested()

    add_mock.assert_called_once()

    created_file = add_mock.call_args.kwargs["file"]

    assert created_file is not None


# =============================================================================
# CERRAR ARCHIVO ACTUAL
# =============================================================================


def test_close_current_file_without_editor(
    sql_editor_area,
    mocker,
):
    """
    Si no existe editor activo no debe ocurrir nada.
    """

    remove_mock = mocker.patch.object(
        sql_editor_area,
        "_remove_file_and_editor",
    )

    mocker.patch.object(
        sql_editor_area,
        "_get_current_editor",
        return_value=None,
    )

    sql_editor_area._on_close_current_file_requested()

    remove_mock.assert_not_called()


def test_close_current_file(
    sql_editor_area,
    fake_editor,
    fake_file,
    mocker,
):
    """
    Debe cerrar el archivo asociado al editor actual.
    """

    remove_mock = mocker.patch.object(
        sql_editor_area,
        "_remove_file_and_editor",
    )

    mocker.patch.object(
        sql_editor_area,
        "_get_current_editor",
        return_value=fake_editor,
    )

    sql_editor_area._on_close_current_file_requested()

    remove_mock.assert_called_once_with(fake_file)


# =============================================================================
# ABRIR ARCHIVO
# =============================================================================


def test_open_file_dialog_cancelled(
    sql_editor_area,
    open_dialog_mock,
    open_file_mock,
):
    """
    Cancelar el diálogo no debe intentar abrir ningún archivo.
    """

    open_dialog_mock.return_value = (
        "",
        "",
    )

    sql_editor_area._on_open_file_requested()

    open_file_mock.assert_not_called()


def test_open_file_service_returns_none(
    sql_editor_area,
    open_dialog_mock,
    open_file_mock,
    notify_mock,
):
    """
    Si el servicio devuelve None debe notificarse un error.
    """

    open_dialog_mock.return_value = (
        "/tmp/query.sql",
        "",
    )

    open_file_mock.return_value = None

    sql_editor_area._on_open_file_requested()

    open_file_mock.assert_called_once()

    notify_mock.assert_called_once()


def test_open_file_already_open(
    sql_editor_area,
    fake_file,
    open_dialog_mock,
    open_file_mock,
    mocker,
):
    """
    Si el archivo ya está abierto debe mostrarse su editor.
    """

    open_dialog_mock.return_value = (
        "/tmp/query.sql",
        "",
    )

    open_file_mock.return_value = fake_file

    sql_editor_area.files = [
        fake_file,
    ]

    show_mock = mocker.patch.object(
        sql_editor_area,
        "_show_editor",
    )

    add_mock = mocker.patch.object(
        sql_editor_area,
        "_add_file_and_editor",
    )

    sql_editor_area._on_open_file_requested()

    show_mock.assert_called_once_with(fake_file)

    add_mock.assert_not_called()


def test_open_file_new(
    sql_editor_area,
    fake_file,
    open_dialog_mock,
    open_file_mock,
    mocker,
):
    """
    Si el archivo no estaba abierto debe añadirse.
    """

    open_dialog_mock.return_value = (
        "/tmp/query.sql",
        "",
    )

    open_file_mock.return_value = fake_file

    add_mock = mocker.patch.object(
        sql_editor_area,
        "_add_file_and_editor",
    )

    show_mock = mocker.patch.object(
        sql_editor_area,
        "_show_editor",
    )

    sql_editor_area._on_open_file_requested()

    add_mock.assert_called_once_with(fake_file)

    show_mock.assert_not_called()


@pytest.mark.parametrize(
    "opened_path",
    [
        Path("/tmp/query.sql"),
        Path("/tmp/../tmp/query.sql"),
    ],
)
def test_open_file_detects_same_path(
    sql_editor_area,
    fake_file,
    open_dialog_mock,
    open_file_mock,
    mocker,
    opened_path,
):
    """
    Si existe un File con la misma ruta debe reutilizarse.
    """

    fake_file.path = opened_path

    opened = MagicMock()
    opened.path = opened_path

    sql_editor_area.files = [
        fake_file,
    ]

    open_dialog_mock.return_value = (
        str(opened_path),
        "",
    )

    open_file_mock.return_value = opened

    show_mock = mocker.patch.object(
        sql_editor_area,
        "_show_editor",
    )

    add_mock = mocker.patch.object(
        sql_editor_area,
        "_add_file_and_editor",
    )

    sql_editor_area._on_open_file_requested()

    show_mock.assert_called_once_with(fake_file)

    add_mock.assert_not_called()


# =============================================================================
# GUARDAR ARCHIVO
# =============================================================================


def test_save_file_without_current_editor(
    sql_editor_area,
    mocker,
):
    """
    Si no existe editor activo no debe hacerse nada.
    """

    mocker.patch.object(
        sql_editor_area,
        "_get_current_editor",
        return_value=None,
    )

    save_mock = mocker.patch(
        "ui.widgets.workspace.sql_editor.sql_editor_area.files_service.save_file",
    )

    sql_editor_area._on_save_file_requested()

    save_mock.assert_not_called()


def test_save_specific_file_without_editor(
    sql_editor_area,
    fake_file,
    mocker,
):
    """
    Si se proporciona un File pero no existe editor asociado no debe hacerse nada.
    """

    mocker.patch.object(
        sql_editor_area,
        "_get_editor",
        return_value=None,
    )

    save_mock = mocker.patch(
        "ui.widgets.workspace.sql_editor.sql_editor_area.files_service.save_file",
    )

    sql_editor_area._on_save_file_requested(fake_file)

    save_mock.assert_not_called()


def test_save_new_file_cancel_dialog(
    sql_editor_area,
    fake_editor,
    save_dialog_mock,
    save_file_mock,
    mocker,
):
    """
    Cancelar el diálogo de guardar debe abortar el guardado.
    """

    fake_editor.file.path = None

    mocker.patch.object(
        sql_editor_area,
        "_get_current_editor",
        return_value=fake_editor,
    )

    save_dialog_mock.return_value = (
        "",
        "",
    )

    sql_editor_area._on_save_file_requested()

    save_file_mock.assert_not_called()


def test_save_new_file_success(
    sql_editor_area,
    fake_editor,
    fake_file,
    save_dialog_mock,
    save_file_mock,
    notify_mock,
    mocker,
):
    """
    Guardado correcto de un archivo nuevo.
    """

    fake_file.path = None

    save_dialog_mock.return_value = (
        "/tmp/query.sql",
        "",
    )

    save_file_mock.return_value = True

    mocker.patch.object(
        sql_editor_area,
        "_get_current_editor",
        return_value=fake_editor,
    )

    refresh_mock = mocker.patch.object(
        sql_editor_area.files_list,
        "refresh_file",
    )

    fake_file.change_path = mocker.Mock()

    sql_editor_area._on_save_file_requested()

    fake_file.change_path.assert_called_once()

    save_file_mock.assert_called_once_with(fake_file)

    refresh_mock.assert_called_once_with(fake_file)

    notify_mock.assert_called_once()


@pytest.mark.parametrize(
    "save_result",
    [
        True,
        False,
    ],
)
def test_save_existing_file(
    sql_editor_area,
    fake_editor,
    fake_file,
    save_result,
    notify_mock,
    save_file_mock,
    mocker,
):
    """
    Guarda un archivo existente con cambios.
    """

    fake_file.path = Path("/tmp/query.sql")
    fake_file.has_changes = True

    save_file_mock.return_value = save_result

    mocker.patch.object(
        sql_editor_area,
        "_get_current_editor",
        return_value=fake_editor,
    )

    refresh_mock = mocker.patch.object(
        sql_editor_area.files_list,
        "refresh_file",
    )

    sql_editor_area._on_save_file_requested()

    save_file_mock.assert_called_once_with(fake_file)

    if save_result:
        refresh_mock.assert_called_once_with(fake_file)
    else:
        refresh_mock.assert_not_called()

    notify_mock.assert_called_once()


def test_save_existing_file_without_changes(
    sql_editor_area,
    fake_editor,
    fake_file,
    notify_mock,
    save_file_mock,
    mocker,
):
    """
    Si no existen cambios no debe guardarse el archivo.
    """

    fake_file.path = Path("/tmp/query.sql")
    fake_file.has_changes = False

    mocker.patch.object(
        sql_editor_area,
        "_get_current_editor",
        return_value=fake_editor,
    )

    sql_editor_area._on_save_file_requested()

    save_file_mock.assert_not_called()

    notify_mock.assert_called_once()


def test_save_specific_file(
    sql_editor_area,
    fake_editor,
    fake_file,
    save_file_mock,
    notify_mock,
    mocker,
):
    """
    Si se proporciona un File debe utilizarse su editor asociado.
    """

    fake_file.has_changes = True

    save_file_mock.return_value = True

    mocker.patch.object(
        sql_editor_area,
        "_get_editor",
        return_value=fake_editor,
    )

    refresh_mock = mocker.patch.object(
        sql_editor_area.files_list,
        "refresh_file",
    )

    sql_editor_area._on_save_file_requested(fake_file)

    save_file_mock.assert_called_once_with(fake_file)

    refresh_mock.assert_called_once_with(fake_file)

    notify_mock.assert_called_once()


# =============================================================================
# RENOMBRAR ARCHIVO
# =============================================================================


def test_rename_without_current_editor(
    sql_editor_area,
    rename_dialog_mock,
    mocker,
):
    """
    Si no existe editor activo no debe abrirse el diálogo.
    """

    mocker.patch.object(
        sql_editor_area,
        "_get_current_editor",
        return_value=None,
    )

    sql_editor_area._on_rename_file_requested()

    rename_dialog_mock.assert_not_called()


def test_rename_specific_file_without_editor(
    sql_editor_area,
    fake_file,
    rename_dialog_mock,
    mocker,
):
    """
    Si no existe editor asociado al File indicado no debe hacerse nada.
    """

    mocker.patch.object(
        sql_editor_area,
        "_get_editor",
        return_value=None,
    )

    sql_editor_area._on_rename_file_requested(fake_file)

    rename_dialog_mock.assert_not_called()


def test_rename_cancelled(
    sql_editor_area,
    fake_editor,
    fake_file,
    rename_dialog_mock,
    mocker,
):
    """
    Cancelar el diálogo no debe renombrar el archivo.
    """

    rename_dialog_mock.return_value = None

    mocker.patch.object(
        sql_editor_area,
        "_get_current_editor",
        return_value=fake_editor,
    )

    fake_file.rename = mocker.Mock()

    refresh_mock = mocker.patch.object(
        sql_editor_area.files_list,
        "refresh_file",
    )

    sql_editor_area._on_rename_file_requested()

    fake_file.rename.assert_not_called()

    refresh_mock.assert_not_called()


def test_rename_success(
    sql_editor_area,
    fake_editor,
    fake_file,
    rename_dialog_mock,
    mocker,
):
    """
    Renombrado correcto.
    """

    rename_dialog_mock.return_value = "new_name.sql"

    mocker.patch.object(
        sql_editor_area,
        "_get_current_editor",
        return_value=fake_editor,
    )

    fake_file.rename = mocker.Mock()

    refresh_mock = mocker.patch.object(
        sql_editor_area.files_list,
        "refresh_file",
    )

    sql_editor_area._on_rename_file_requested()

    fake_file.rename.assert_called_once_with(
        "new_name.sql",
    )

    refresh_mock.assert_called_once_with(
        fake_file,
    )


def test_rename_specific_file(
    sql_editor_area,
    fake_editor,
    fake_file,
    rename_dialog_mock,
    mocker,
):
    """
    Debe utilizar el editor asociado al File recibido.
    """

    rename_dialog_mock.return_value = "other.sql"

    mocker.patch.object(
        sql_editor_area,
        "_get_editor",
        return_value=fake_editor,
    )

    fake_file.rename = mocker.Mock()

    refresh_mock = mocker.patch.object(
        sql_editor_area.files_list,
        "refresh_file",
    )

    sql_editor_area._on_rename_file_requested(fake_file)

    fake_file.rename.assert_called_once_with(
        "other.sql",
    )

    refresh_mock.assert_called_once_with(fake_file)


# =============================================================================
# _ADD_FILE_AND_EDITOR
# =============================================================================


def test_add_file_and_editor(
    sql_editor_area,
    fake_file,
    mocker,
):
    """
    Comprueba la creación del editor y su registro.
    """

    fake_editor = mocker.Mock()
    fake_editor.file = fake_file

    sql_editor_cls = mocker.patch(
        "ui.widgets.workspace.sql_editor.sql_editor_area.SqlEditor",
        return_value=fake_editor,
    )

    add_file_mock = mocker.patch.object(
        sql_editor_area.files_list,
        "add_file",
    )

    add_widget_mock = mocker.patch.object(
        sql_editor_area.editors,
        "addWidget",
    )

    set_current_mock = mocker.patch.object(
        sql_editor_area.editors,
        "setCurrentWidget",
    )

    sql_editor_area._add_file_and_editor(fake_file)

    sql_editor_cls.assert_called_once_with(
        file=fake_file,
    )

    assert fake_file in sql_editor_area.files

    add_file_mock.assert_called_once_with(fake_file)

    add_widget_mock.assert_called_once_with(fake_editor)

    set_current_mock.assert_called_once_with(fake_editor)

    fake_editor.execute_requested.connect.assert_called_once()

    fake_editor.file_modified.connect.assert_called_once()

    fake_editor.save_changes.connect.assert_called_once()

    fake_editor.rename_file.connect.assert_called_once()


# =============================================================================
# _GET_EDITOR
# =============================================================================


def test_get_editor_found(
    sql_editor_area,
    fake_file,
    fake_editor,
    mocker,
):
    """
    Debe devolver el editor asociado.
    """

    mocker.patch.object(
        sql_editor_area.editors,
        "count",
        return_value=1,
    )

    mocker.patch.object(
        sql_editor_area.editors,
        "widget",
        return_value=fake_editor,
    )

    assert sql_editor_area._get_editor(fake_file) is fake_editor


def test_get_editor_not_found(
    sql_editor_area,
    fake_editor,
    fake_file,
    mocker,
):
    """
    Si no existe editor debe devolver None.
    """

    other = mocker.Mock()

    fake_editor.file = other

    mocker.patch.object(
        sql_editor_area.editors,
        "count",
        return_value=1,
    )

    mocker.patch.object(
        sql_editor_area.editors,
        "widget",
        return_value=fake_editor,
    )

    assert sql_editor_area._get_editor(fake_file) is None


# =============================================================================
# _SHOW_EDITOR
# =============================================================================


def test_show_editor_found(
    sql_editor_area,
    fake_editor,
    fake_file,
    mocker,
):
    """
    Debe activar el editor encontrado.
    """

    mocker.patch.object(
        sql_editor_area,
        "_get_editor",
        return_value=fake_editor,
    )

    current_mock = mocker.patch.object(
        sql_editor_area.editors,
        "setCurrentWidget",
    )

    sql_editor_area._show_editor(fake_file)

    current_mock.assert_called_once_with(fake_editor)


def test_show_editor_not_found(
    sql_editor_area,
    fake_file,
    mocker,
):
    """
    Si no existe editor no debe cambiarse el editor activo.
    """

    mocker.patch.object(
        sql_editor_area,
        "_get_editor",
        return_value=None,
    )

    current_mock = mocker.patch.object(
        sql_editor_area.editors,
        "setCurrentWidget",
    )

    sql_editor_area._show_editor(fake_file)

    current_mock.assert_not_called()


# =============================================================================
# _GET_CURRENT_EDITOR
# =============================================================================


def test_get_current_editor(
    sql_editor_area,
    mocker,
):
    """
    Debe devolver el widget actual del stack.
    """

    editor = MagicMock()

    mocker.patch.object(
        sql_editor_area.editors,
        "currentWidget",
        return_value=editor,
    )

    assert sql_editor_area._get_current_editor() is editor


# =============================================================================
# REMOVE FILE AND EDITOR
# =============================================================================


def test_remove_file_and_editor_cancel_confirmation(
    sql_editor_area,
    fake_file,
    confirmation_dialog_mock,
    mocker,
):
    """
    Si el usuario cancela el diálogo de confirmación no debe eliminarse nada.
    """

    fake_file.has_changes = True

    confirmation_dialog_mock.exec.return_value = False

    remove_file_mock = mocker.patch.object(
        sql_editor_area.files_list,
        "remove_file",
    )

    sql_editor_area._remove_file_and_editor(fake_file)

    remove_file_mock.assert_not_called()


def test_remove_file_and_editor_without_editor(
    sql_editor_area,
    fake_file,
    mocker,
):
    """
    Si no existe editor asociado debe finalizar silenciosamente.
    """

    fake_file.has_changes = False

    mocker.patch.object(
        sql_editor_area,
        "_get_editor",
        return_value=None,
    )

    remove_file_mock = mocker.patch.object(
        sql_editor_area.files_list,
        "remove_file",
    )

    sql_editor_area._remove_file_and_editor(fake_file)

    remove_file_mock.assert_not_called()


@pytest.mark.parametrize(
    "was_current",
    [
        True,
        False,
    ],
)
def test_remove_file_and_editor(
    sql_editor_area,
    fake_file,
    fake_editor,
    was_current,
    mocker,
):
    """
    Elimina correctamente un archivo y su editor asociado.
    """

    fake_file.has_changes = False

    sql_editor_area.files = [fake_file]

    mocker.patch.object(
        sql_editor_area,
        "_get_editor",
        return_value=fake_editor,
    )

    if was_current:
        current_editor = fake_editor
    else:
        current_editor = mocker.Mock()

    mocker.patch.object(
        sql_editor_area,
        "_get_current_editor",
        return_value=current_editor,
    )

    remove_file_mock = mocker.patch.object(
        sql_editor_area.files_list,
        "remove_file",
    )

    select_first_mock = mocker.patch.object(
        sql_editor_area.files_list,
        "select_first_file",
    )

    remove_widget_mock = mocker.patch.object(
        sql_editor_area.editors,
        "removeWidget",
    )

    fake_editor.deleteLater = mocker.Mock()

    sql_editor_area._remove_file_and_editor(fake_file)

    remove_file_mock.assert_called_once_with(fake_file)

    remove_widget_mock.assert_called_once_with(fake_editor)

    fake_editor.deleteLater.assert_called_once()

    assert fake_file not in sql_editor_area.files

    if was_current:
        select_first_mock.assert_called_once()
    else:
        select_first_mock.assert_not_called()


def test_remove_file_and_editor_after_confirmation(
    sql_editor_area,
    fake_file,
    fake_editor,
    confirmation_dialog_mock,
    mocker,
):
    """
    Si el usuario acepta el diálogo debe continuar el flujo normal.
    """

    fake_file.has_changes = True

    sql_editor_area.files = [fake_file]

    confirmation_dialog_mock.exec.return_value = True

    mocker.patch.object(
        sql_editor_area,
        "_get_editor",
        return_value=fake_editor,
    )

    mocker.patch.object(
        sql_editor_area,
        "_get_current_editor",
        return_value=fake_editor,
    )

    remove_file_mock = mocker.patch.object(
        sql_editor_area.files_list,
        "remove_file",
    )

    mocker.patch.object(
        sql_editor_area.editors,
        "removeWidget",
    )

    fake_editor.deleteLater = mocker.Mock()

    sql_editor_area._remove_file_and_editor(fake_file)

    remove_file_mock.assert_called_once()


# =============================================================================
# SET QUERY TEXT
# =============================================================================


def test_set_query_text(
    sql_editor_area,
    fake_editor,
    mocker,
):
    """
    Inserta texto en el editor activo.
    """

    mocker.patch.object(
        sql_editor_area,
        "_get_current_editor",
        return_value=fake_editor,
    )

    sql_editor_area.set_query_text("SELECT * FROM table;")

    fake_editor.insert_query_at_cursor.assert_called_once_with("SELECT * FROM table;")


def test_set_query_text_without_editor(
    sql_editor_area,
    mocker,
):
    """
    Si no existe editor activo debe registrarse un warning.
    """

    mocker.patch.object(
        sql_editor_area,
        "_get_current_editor",
        return_value=None,
    )

    logger_mock = mocker.patch("ui.widgets.workspace.sql_editor.sql_editor_area.logger")

    sql_editor_area.set_query_text("SELECT 1")

    logger_mock.warning.assert_called_once()


# =============================================================================
# GET UNSAVED CHANGES COUNT
# =============================================================================


def test_get_unsaved_changes_count(
    sql_editor_area,
    mocker,
):
    """
    Debe contar únicamente los archivos modificados existentes en disco.
    """

    file1 = mocker.Mock(
        has_changes=True,
        existsOnDisk=True,
    )

    file2 = mocker.Mock(
        has_changes=True,
        existsOnDisk=False,
    )

    file3 = mocker.Mock(
        has_changes=False,
        existsOnDisk=True,
    )

    file4 = mocker.Mock(
        has_changes=True,
        existsOnDisk=True,
    )

    sql_editor_area.files = [
        file1,
        file2,
        file3,
        file4,
    ]

    assert sql_editor_area.get_unsaved_changes_count() == 2


def test_get_unsaved_changes_count_empty(
    sql_editor_area,
):
    """
    Sin archivos abiertos debe devolver cero.
    """

    assert sql_editor_area.get_unsaved_changes_count() == 0

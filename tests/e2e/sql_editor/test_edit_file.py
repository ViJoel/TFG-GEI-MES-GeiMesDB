from pathlib import Path

import pytest
from PySide6.QtWidgets import QFileDialog
from pytestqt.qtbot import QtBot

from modules.files import service as files_service
from tests.e2e.data.connections import POSTGRESQL_CONNECTION
from tests.e2e.data.files import (
    FILE_SQL,
    FILE_TXT,
)
from tests.e2e.utils.functions import (
    auto_accept_confirmation_dialog,
    connect_to_db,
    disconnect_from_db,
    get_sql_editor_area,
    open_file,
)
from ui.app.main_window import MainWindow

# =============================================================================
# VARIABLES
# =============================================================================

SQL_FILE_CONTENT = "SELECT 1;\n"
SQL_FILE_CONTENT_EDITED = "SELECT 2;\n"
TXT_FILE_CONTENT = "This is a text file.\n"
TXT_FILE_CONTENT_EDITED = "This content has been edited.\n"


# =============================================================================
# TESTS
# =============================================================================


def test_edit_sql_file_success(
    qtbot: QtBot,
    main_window: MainWindow,
    temporary_sql_directory: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """
    Verifica que se puede abrir, editar y guardar
    correctamente un archivo .sql.
    """

    file_path = temporary_sql_directory / FILE_SQL
    file_path.write_text(
        SQL_FILE_CONTENT,
        encoding="utf-8",
    )

    connect_to_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=POSTGRESQL_CONNECTION.name,
    )

    sql_editor_area = get_sql_editor_area(
        main_window,
        POSTGRESQL_CONNECTION,
    )

    editor = open_file(
        qtbot=qtbot,
        sql_editor_area=sql_editor_area,
        file_path=file_path,
        monkeypatch=monkeypatch,
    )

    assert editor is not None
    assert editor.file.path == file_path
    assert editor.file.content == SQL_FILE_CONTENT

    editor.setPlainText(SQL_FILE_CONTENT_EDITED)

    sql_editor_area.toolbar.save_button.click()

    assert file_path.read_text(encoding="utf-8") == SQL_FILE_CONTENT_EDITED

    disconnect_from_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=POSTGRESQL_CONNECTION.name,
    )


def test_edit_txt_file_success(
    qtbot: QtBot,
    main_window: MainWindow,
    temporary_sql_directory: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """
    Verifica que se puede abrir, editar y guardar
    correctamente un archivo .txt.
    """

    file_path = temporary_sql_directory / FILE_TXT
    file_path.write_text(
        TXT_FILE_CONTENT,
        encoding="utf-8",
    )

    connect_to_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=POSTGRESQL_CONNECTION.name,
    )

    sql_editor_area = get_sql_editor_area(
        main_window,
        POSTGRESQL_CONNECTION,
    )

    editor = open_file(
        qtbot=qtbot,
        sql_editor_area=sql_editor_area,
        file_path=file_path,
        monkeypatch=monkeypatch,
    )

    assert editor is not None
    assert editor.file.path == file_path
    assert editor.file.content == TXT_FILE_CONTENT

    editor.setPlainText(TXT_FILE_CONTENT_EDITED)

    sql_editor_area.toolbar.save_button.click()

    assert file_path.read_text(encoding="utf-8") == TXT_FILE_CONTENT_EDITED

    disconnect_from_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=POSTGRESQL_CONNECTION.name,
    )


def test_edit_sql_file_open_error(
    qtbot: QtBot,
    main_window: MainWindow,
    temporary_sql_directory: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """
    Verifica que se gestiona correctamente un error
    al abrir un archivo .sql.
    """

    file_path = temporary_sql_directory / FILE_SQL

    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileName",
        lambda *args, **kwargs: (
            str(file_path),
            "SQL Files (*.sql)",
        ),
    )

    monkeypatch.setattr(
        files_service,
        "open_file",
        lambda path: None,
    )

    connect_to_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=POSTGRESQL_CONNECTION.name,
    )

    sql_editor_area = get_sql_editor_area(
        main_window,
        POSTGRESQL_CONNECTION,
    )

    sql_editor_area.toolbar.open_button.click()

    assert sql_editor_area._get_current_editor() is None
    assert not sql_editor_area.files

    disconnect_from_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=POSTGRESQL_CONNECTION.name,
    )


def test_edit_txt_file_open_error(
    qtbot: QtBot,
    main_window: MainWindow,
    temporary_sql_directory: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """
    Verifica que se gestiona correctamente un error
    al abrir un archivo .txt.
    """

    file_path = temporary_sql_directory / FILE_TXT

    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileName",
        lambda *args, **kwargs: (
            str(file_path),
            "Text Files (*.txt)",
        ),
    )

    monkeypatch.setattr(
        files_service,
        "open_file",
        lambda path: None,
    )

    connect_to_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=POSTGRESQL_CONNECTION.name,
    )

    sql_editor_area = get_sql_editor_area(
        main_window,
        POSTGRESQL_CONNECTION,
    )

    sql_editor_area.toolbar.open_button.click()

    assert sql_editor_area._get_current_editor() is None
    assert not sql_editor_area.files

    disconnect_from_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=POSTGRESQL_CONNECTION.name,
    )


def test_edit_sql_file_save_error(
    qtbot: QtBot,
    main_window: MainWindow,
    temporary_sql_directory: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """
    Verifica que se gestiona correctamente un error
    al guardar un archivo .sql previamente abierto.
    """

    file_path = temporary_sql_directory / FILE_SQL

    file_path.write_text(
        SQL_FILE_CONTENT,
        encoding="utf-8",
    )

    monkeypatch.setattr(
        files_service,
        "save_file",
        lambda file: False,
    )

    connect_to_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=POSTGRESQL_CONNECTION.name,
    )

    sql_editor_area = get_sql_editor_area(
        main_window,
        POSTGRESQL_CONNECTION,
    )

    editor = open_file(
        qtbot=qtbot,
        sql_editor_area=sql_editor_area,
        file_path=file_path,
        monkeypatch=monkeypatch,
    )

    editor.setPlainText(SQL_FILE_CONTENT_EDITED)

    sql_editor_area.toolbar.save_button.click()

    assert file_path.read_text(encoding="utf-8") == SQL_FILE_CONTENT

    disconnect_from_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=POSTGRESQL_CONNECTION.name,
    )


def test_edit_txt_file_save_error(
    qtbot: QtBot,
    main_window: MainWindow,
    temporary_sql_directory: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """
    Verifica que se gestiona correctamente un error
    al guardar un archivo .txt previamente abierto.
    """

    file_path = temporary_sql_directory / FILE_TXT

    file_path.write_text(
        TXT_FILE_CONTENT,
        encoding="utf-8",
    )

    monkeypatch.setattr(
        files_service,
        "save_file",
        lambda file: False,
    )

    connect_to_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=POSTGRESQL_CONNECTION.name,
    )

    sql_editor_area = get_sql_editor_area(
        main_window,
        POSTGRESQL_CONNECTION,
    )

    editor = open_file(
        qtbot=qtbot,
        sql_editor_area=sql_editor_area,
        file_path=file_path,
        monkeypatch=monkeypatch,
    )

    editor.setPlainText(TXT_FILE_CONTENT_EDITED)

    sql_editor_area.toolbar.save_button.click()

    assert file_path.read_text(encoding="utf-8") == TXT_FILE_CONTENT

    disconnect_from_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=POSTGRESQL_CONNECTION.name,
    )


def test_edit_sql_file_and_close_application(
    qtbot: QtBot,
    main_window: MainWindow,
    temporary_sql_directory: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """
    Verifica que un archivo .sql existente puede abrirse,
    modificarse y que al cerrar la aplicación se solicita
    confirmación por los cambios sin guardar.
    """

    sql_file = temporary_sql_directory / "test.sql"

    sql_file.write_text(
        SQL_FILE_CONTENT,
        encoding="utf-8",
    )

    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileName",
        lambda *args, **kwargs: (
            str(sql_file),
            "SQL Files (*.sql)",
        ),
    )

    connect_to_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=POSTGRESQL_CONNECTION.name,
    )

    workspace = main_window.workspaces[POSTGRESQL_CONNECTION.id]
    sql_editor_area = workspace.sql_editor_area

    # Abrir el archivo existente.
    sql_editor_area.toolbar.open_button.click()

    editor = sql_editor_area._get_current_editor()

    assert editor is not None
    assert editor.file.path == sql_file
    assert editor.toPlainText() == SQL_FILE_CONTENT

    # Modificar el contenido sin guardarlo.
    editor.setPlainText(SQL_FILE_CONTENT_EDITED)

    assert editor.file.has_changes is True
    assert editor.file.existsOnDisk is True

    # Interceptar el diálogo de confirmación de MainWindow.
    auto_accept_confirmation_dialog(monkeypatch)

    # El cierre debe detectar el archivo modificado y
    # aceptar automáticamente el diálogo.
    main_window.close()

    assert sql_file.read_text(encoding="utf-8") == SQL_FILE_CONTENT

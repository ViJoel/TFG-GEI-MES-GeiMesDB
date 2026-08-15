from pathlib import Path

import pytest
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QFileDialog
from pytestqt.qtbot import QtBot

from tests.e2e.data.connections import POSTGRESQL_CONNECTION
from tests.e2e.data.files import (
    FILE_SQL,
    FILE_SQL_CONTENT,
    FILE_TXT,
    FILE_TXT_CONTENT,
)
from tests.e2e.utils.functions import (
    connect_to_db,
    disconnect_from_db,
    get_sql_editor_area,
    open_file,
)
from ui.app.main_window import MainWindow
from ui.widgets.workspace.sql_editor.rename_file_dialog import RenameFileDialog

# =============================================================================
# FUNCTIONS
# =============================================================================


def rename_file(
    monkeypatch: pytest.MonkeyPatch,
    new_name: str,
) -> None:
    """
    Intercepta el diálogo de renombramiento y devuelve
    automáticamente el nuevo nombre indicado.
    """

    monkeypatch.setattr(
        RenameFileDialog,
        "get_new_name",
        lambda *args, **kwargs: new_name,
    )


# =============================================================================
# TESTS
# =============================================================================


def test_rename_sql_file(
    qtbot: QtBot,
    main_window: MainWindow,
    temporary_sql_directory: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """
    Verifica que renombrar un archivo .sql sin cambiar su extensión
    actualiza el nombre del archivo tanto en la interfaz como en disco.
    """

    connect_to_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=POSTGRESQL_CONNECTION.name,
    )

    renamed_file_name = "renamed.sql"
    file_path = temporary_sql_directory / FILE_SQL
    renamed_file_path = temporary_sql_directory / renamed_file_name

    sql_editor_area = get_sql_editor_area(
        main_window=main_window,
        connection=POSTGRESQL_CONNECTION,
    )

    editor = open_file(
        qtbot=qtbot,
        sql_editor_area=sql_editor_area,
        file_path=file_path,
        monkeypatch=monkeypatch,
    )

    assert editor is not None
    assert editor.file.name == FILE_SQL
    assert editor.file.path == file_path
    assert file_path.exists()

    rename_file(
        monkeypatch=monkeypatch,
        new_name=renamed_file_name,
    )

    sql_editor_area.toolbar.rename_button.click()

    assert file_path.exists()
    assert not renamed_file_path.exists()

    sql_editor_area.toolbar.save_button.click()

    assert editor.file.name == renamed_file_name
    assert editor.file.path == renamed_file_path

    assert not file_path.exists()
    assert renamed_file_path.exists()

    assert (
        renamed_file_path.read_text(
            encoding="utf-8",
        )
        == FILE_SQL_CONTENT
    )

    disconnect_from_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=POSTGRESQL_CONNECTION.name,
    )


def test_rename_sql_file_to_txt(
    qtbot: QtBot,
    main_window: MainWindow,
    temporary_sql_directory: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """
    Verifica que renombrar un archivo .sql cambiando su extensión a .txt
    actualiza el nombre del archivo y su extensión tanto en la interfaz
    como en disco.
    """

    connect_to_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=POSTGRESQL_CONNECTION.name,
    )

    renamed_file_name = "renamed.txt"
    file_path = temporary_sql_directory / FILE_SQL
    renamed_file_path = temporary_sql_directory / renamed_file_name

    sql_editor_area = get_sql_editor_area(
        main_window=main_window,
        connection=POSTGRESQL_CONNECTION,
    )

    editor = open_file(
        qtbot=qtbot,
        sql_editor_area=sql_editor_area,
        file_path=file_path,
        monkeypatch=monkeypatch,
    )

    assert editor is not None
    assert editor.file.name == FILE_SQL
    assert editor.file.path == file_path
    assert file_path.exists()

    rename_file(
        monkeypatch=monkeypatch,
        new_name=renamed_file_name,
    )

    sql_editor_area.toolbar.rename_button.click()

    assert file_path.exists()
    assert not renamed_file_path.exists()

    sql_editor_area.toolbar.save_button.click()

    assert editor.file.name == renamed_file_name
    assert editor.file.path == renamed_file_path

    assert not file_path.exists()
    assert renamed_file_path.exists()

    assert (
        renamed_file_path.read_text(
            encoding="utf-8",
        )
        == FILE_SQL_CONTENT
    )

    disconnect_from_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=POSTGRESQL_CONNECTION.name,
    )


def test_rename_sql_file_to_unsupported_extension(
    qtbot: QtBot,
    main_window: MainWindow,
    temporary_sql_directory: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """
    Verifica que al introducir una extensión no soportada
    durante el renombrado de un archivo, la aplicación
    aplica automáticamente la extensión .sql.
    """

    connect_to_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=POSTGRESQL_CONNECTION.name,
    )

    attempted_file_name = "renamed.py"
    expected_file_name = "renamed.py.sql"

    file_path = temporary_sql_directory / FILE_SQL
    renamed_file_path = temporary_sql_directory / expected_file_name

    sql_editor_area = get_sql_editor_area(
        main_window=main_window,
        connection=POSTGRESQL_CONNECTION,
    )

    editor = open_file(
        qtbot=qtbot,
        sql_editor_area=sql_editor_area,
        file_path=file_path,
        monkeypatch=monkeypatch,
    )

    assert editor is not None
    assert editor.file.name == FILE_SQL
    assert editor.file.path == file_path
    assert file_path.exists()

    def fill_rename_dialog() -> None:
        dialog = main_window.findChild(RenameFileDialog)

        assert dialog is not None

        dialog.setTextValue(attempted_file_name)
        dialog.accept()

    QTimer.singleShot(
        0,
        fill_rename_dialog,
    )

    sql_editor_area.toolbar.rename_button.click()

    assert file_path.exists()
    assert not renamed_file_path.exists()

    sql_editor_area.toolbar.save_button.click()

    assert editor.file.name == expected_file_name
    assert editor.file.path == renamed_file_path

    assert not file_path.exists()
    assert renamed_file_path.exists()

    assert (
        renamed_file_path.read_text(
            encoding="utf-8",
        )
        == FILE_SQL_CONTENT
    )

    disconnect_from_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=POSTGRESQL_CONNECTION.name,
    )


def test_rename_sql_file_without_extension(
    qtbot: QtBot,
    main_window: MainWindow,
    temporary_sql_directory: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """
    Verifica que renombrar un archivo .sql sin indicar una extensión
    añade automáticamente la extensión .sql.
    """

    connect_to_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=POSTGRESQL_CONNECTION.name,
    )

    renamed_file_name_try = "renamed"
    renamed_file_name = "renamed.sql"

    file_path = temporary_sql_directory / FILE_SQL
    renamed_file_path = temporary_sql_directory / renamed_file_name

    sql_editor_area = get_sql_editor_area(
        main_window=main_window,
        connection=POSTGRESQL_CONNECTION,
    )

    editor = open_file(
        qtbot=qtbot,
        sql_editor_area=sql_editor_area,
        file_path=file_path,
        monkeypatch=monkeypatch,
    )

    assert editor is not None
    assert editor.file.name == FILE_SQL
    assert editor.file.path == file_path
    assert file_path.exists()

    rename_file(
        monkeypatch=monkeypatch,
        new_name=renamed_file_name_try,
    )

    sql_editor_area.toolbar.rename_button.click()

    assert file_path.exists()
    assert not renamed_file_path.exists()

    sql_editor_area.toolbar.save_button.click()

    assert editor.file.name == renamed_file_name
    assert editor.file.path == renamed_file_path

    assert not file_path.exists()
    assert renamed_file_path.exists()

    assert (
        renamed_file_path.read_text(
            encoding="utf-8",
        )
        == FILE_SQL_CONTENT
    )

    disconnect_from_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=POSTGRESQL_CONNECTION.name,
    )


def test_rename_txt_file_to_sql_extension(
    qtbot: QtBot,
    main_window: MainWindow,
    temporary_sql_directory: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """
    Verifica que renombrar un archivo .txt a un nombre con
    extensión .sql actualiza correctamente el nombre del archivo
    tanto en la interfaz como en disco.
    """

    connect_to_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=POSTGRESQL_CONNECTION.name,
    )

    renamed_file_name = "renamed.sql"

    file_path = temporary_sql_directory / FILE_TXT
    renamed_file_path = temporary_sql_directory / renamed_file_name

    sql_editor_area = get_sql_editor_area(
        main_window=main_window,
        connection=POSTGRESQL_CONNECTION,
    )

    editor = open_file(
        qtbot=qtbot,
        sql_editor_area=sql_editor_area,
        file_path=file_path,
        monkeypatch=monkeypatch,
    )

    assert editor is not None
    assert editor.file.name == FILE_TXT
    assert editor.file.path == file_path
    assert file_path.exists()

    rename_file(
        monkeypatch=monkeypatch,
        new_name=renamed_file_name,
    )

    sql_editor_area.toolbar.rename_button.click()

    assert file_path.exists()
    assert not renamed_file_path.exists()

    sql_editor_area.toolbar.save_button.click()

    assert editor.file.name == renamed_file_name
    assert editor.file.path == renamed_file_path

    assert not file_path.exists()
    assert renamed_file_path.exists()

    assert (
        renamed_file_path.read_text(
            encoding="utf-8",
        )
        == FILE_TXT_CONTENT
    )

    disconnect_from_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=POSTGRESQL_CONNECTION.name,
    )


def test_rename_txt_file_without_extension(
    qtbot: QtBot,
    main_window: MainWindow,
    temporary_sql_directory: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """
    Verifica que renombrar un archivo .txt sin indicar una extensión
    añade automáticamente la extensión .sql.
    """

    connect_to_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=POSTGRESQL_CONNECTION.name,
    )

    renamed_file_name_try = "renamed"
    renamed_file_name = "renamed.sql"

    file_path = temporary_sql_directory / FILE_TXT
    renamed_file_path = temporary_sql_directory / renamed_file_name

    sql_editor_area = get_sql_editor_area(
        main_window=main_window,
        connection=POSTGRESQL_CONNECTION,
    )

    editor = open_file(
        qtbot=qtbot,
        sql_editor_area=sql_editor_area,
        file_path=file_path,
        monkeypatch=monkeypatch,
    )

    assert editor is not None
    assert editor.file.name == FILE_TXT
    assert editor.file.path == file_path
    assert file_path.exists()

    rename_file(
        monkeypatch=monkeypatch,
        new_name=renamed_file_name_try,
    )

    sql_editor_area.toolbar.rename_button.click()

    assert file_path.exists()
    assert not renamed_file_path.exists()

    sql_editor_area.toolbar.save_button.click()

    assert editor.file.name == renamed_file_name
    assert editor.file.path == renamed_file_path

    assert not file_path.exists()
    assert renamed_file_path.exists()

    assert (
        renamed_file_path.read_text(
            encoding="utf-8",
        )
        == FILE_TXT_CONTENT
    )

    disconnect_from_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=POSTGRESQL_CONNECTION.name,
    )

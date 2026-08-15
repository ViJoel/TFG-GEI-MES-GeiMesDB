from pathlib import Path

import pytest
from PySide6.QtWidgets import QFileDialog
from pytestqt.qtbot import QtBot

from modules.files import service as files_service
from tests.e2e.data.connections import POSTGRESQL_CONNECTION
from tests.e2e.utils.functions import (
    connect_to_db,
    disconnect_from_db,
)
from ui.app.main_window import MainWindow

# =============================================================================
# TESTS
# =============================================================================


def test_create_file_success(
    qtbot: QtBot,
    main_window: MainWindow,
    temporary_sql_directory: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """
    Verifica que se crea un archivo .sql correctamente.
    """

    created_file = temporary_sql_directory / "created.sql"

    file_text = "SELECT 1;\n"

    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        lambda *args, **kwargs: (
            str(created_file),
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

    sql_editor_area.toolbar.new_button.click()

    editor = sql_editor_area._get_current_editor()

    assert editor is not None

    editor.setPlainText(file_text)

    sql_editor_area.toolbar.save_button.click()

    assert created_file.exists()
    assert created_file.read_text(encoding="utf-8") == file_text

    disconnect_from_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=POSTGRESQL_CONNECTION.name,
    )


def test_create_file_error(
    qtbot: QtBot,
    main_window: MainWindow,
    temporary_sql_directory: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """
    Verifica que se gestiona correctamente un error
    al guardar un archivo .sql.
    """

    connect_to_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=POSTGRESQL_CONNECTION.name,
    )

    created_file = temporary_sql_directory / "created.sql"

    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        lambda *args, **kwargs: (
            str(created_file),
            "SQL Files (*.sql)",
        ),
    )

    monkeypatch.setattr(
        files_service,
        "save_file",
        lambda file: False,
    )

    workspace = main_window.workspaces[POSTGRESQL_CONNECTION.id]
    sql_editor_area = workspace.sql_editor_area

    sql_editor_area.toolbar.new_button.click()

    editor = sql_editor_area._get_current_editor()

    assert editor is not None

    editor.setPlainText(
        "SELECT 1;\n",
    )

    sql_editor_area.toolbar.save_button.click()

    assert not created_file.exists()

    disconnect_from_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=POSTGRESQL_CONNECTION.name,
    )

import random

import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QSignalSpy
from pytestqt.qtbot import QtBot

from tests.e2e.data.connections import (
    MYSQL_CONNECTION,
    POSTGRESQL_CONNECTION,
)
from tests.e2e.utils.functions import (
    auto_accept_confirmation_dialog,
    connect_to_db,
    create_new_editor,
    disconnect_from_db,
    get_sql_editor_area,
    get_workspace,
)
from ui.app.main_window import MainWindow

# =============================================================================
# TESTS
# =============================================================================


def test_supported_table_postgresql(
    qtbot: QtBot,
    main_window: MainWindow,
):
    """
    Verifica que todas las columnas de table_supported
    son editables en PostgreSQL.
    """

    connect_to_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=POSTGRESQL_CONNECTION.name,
    )

    workspace = get_workspace(
        main_window=main_window,
        connection=POSTGRESQL_CONNECTION,
    )

    sql_editor_area = get_sql_editor_area(
        main_window=main_window,
        connection=POSTGRESQL_CONNECTION,
    )

    editor = create_new_editor(
        sql_editor_area=sql_editor_area,
    )

    assert editor is not None

    query = "SELECT * FROM table_supported;"

    editor.setPlainText(query)

    sql_editor_area.toolbar.execute_query_button.click()

    results_view = workspace.results_view

    qtbot.waitUntil(
        lambda: results_view.table.model is not None,
        timeout=5000,
    )

    model = results_view.table.model

    assert model is not None

    assert model.result_set.columns == [
        "id",
        "boolean_value",
        "date_value",
        "datetime_value",
        "float_value",
        "integer_value",
        "numeric_value",
        "string_value",
        "time_value",
        "uuid_value",
    ]

    assert model.result_set.rows

    # === EDITABILIDAD ===

    for column in range(model.columnCount()):

        index = model.index(0, column)

        assert index.flags() & Qt.ItemFlag.ItemIsEditable

    disconnect_from_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=POSTGRESQL_CONNECTION.name,
    )


def test_complex_table_postgresql(
    qtbot: QtBot,
    main_window: MainWindow,
):
    """
    Verifica que únicamente la columna id de table_complex
    es editable en PostgreSQL.
    """

    connect_to_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=POSTGRESQL_CONNECTION.name,
    )

    workspace = get_workspace(
        main_window=main_window,
        connection=POSTGRESQL_CONNECTION,
    )

    sql_editor_area = get_sql_editor_area(
        main_window=main_window,
        connection=POSTGRESQL_CONNECTION,
    )

    editor = create_new_editor(
        sql_editor_area=sql_editor_area,
    )

    assert editor is not None

    query = "SELECT * FROM table_complex;"

    editor.setPlainText(query)

    sql_editor_area.toolbar.execute_query_button.click()

    results_view = workspace.results_view

    qtbot.waitUntil(
        lambda: results_view.table.model is not None,
        timeout=5000,
    )

    model = results_view.table.model

    assert model is not None

    assert model.result_set.columns == [
        "id",
        "json_value",
        "array_value",
        "binary_value",
    ]

    assert model.result_set.rows

    # === EDITABILIDAD ===

    id_index = model.index(0, 0)

    assert id_index.flags() & Qt.ItemFlag.ItemIsEditable

    for column in range(1, model.columnCount()):

        index = model.index(0, column)

        assert not index.flags() & Qt.ItemFlag.ItemIsEditable

    disconnect_from_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=POSTGRESQL_CONNECTION.name,
    )


def test_supported_table_mysql(
    qtbot: QtBot,
    main_window: MainWindow,
):
    """
    Verifica que todas las columnas de table_supported
    son editables en MySQL.
    """

    connect_to_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=MYSQL_CONNECTION.name,
    )

    workspace = get_workspace(
        main_window=main_window,
        connection=MYSQL_CONNECTION,
    )

    sql_editor_area = get_sql_editor_area(
        main_window=main_window,
        connection=MYSQL_CONNECTION,
    )

    editor = create_new_editor(
        sql_editor_area=sql_editor_area,
    )

    assert editor is not None

    query = "SELECT * FROM table_supported;"

    editor.setPlainText(query)

    sql_editor_area.toolbar.execute_query_button.click()

    results_view = workspace.results_view

    qtbot.waitUntil(
        lambda: results_view.table.model is not None,
        timeout=5000,
    )

    model = results_view.table.model

    assert model is not None

    assert model.result_set.columns == [
        "id",
        "boolean_value",
        "date_value",
        "datetime_value",
        "float_value",
        "integer_value",
        "numeric_value",
        "string_value",
        "time_value",
        "uuid_value",
    ]

    assert model.result_set.rows

    for column in range(model.columnCount()):

        index = model.index(0, column)

        assert model.flags(index) & Qt.ItemFlag.ItemIsEditable

    disconnect_from_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=MYSQL_CONNECTION.name,
    )


def test_complex_table_mysql(
    qtbot: QtBot,
    main_window: MainWindow,
):
    """
    Verifica que únicamente la columna id de table_complex
    es editable en MySQL.
    """

    connect_to_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=MYSQL_CONNECTION.name,
    )

    workspace = get_workspace(
        main_window=main_window,
        connection=MYSQL_CONNECTION,
    )

    sql_editor_area = get_sql_editor_area(
        main_window=main_window,
        connection=MYSQL_CONNECTION,
    )

    editor = create_new_editor(
        sql_editor_area=sql_editor_area,
    )

    assert editor is not None

    query = "SELECT * FROM table_complex;"

    editor.setPlainText(query)

    sql_editor_area.toolbar.execute_query_button.click()

    results_view = workspace.results_view

    qtbot.waitUntil(
        lambda: results_view.table.model is not None,
        timeout=5000,
    )

    model = results_view.table.model

    assert model is not None

    assert model.result_set.columns == [
        "id",
        "json_value",
        "array_value",
        "binary_value",
    ]

    assert model.result_set.rows

    # === EDITABILIDAD ===

    id_index = model.index(0, 0)

    assert id_index.flags() & Qt.ItemFlag.ItemIsEditable

    for column in range(1, model.columnCount()):

        index = model.index(0, column)

        assert not index.flags() & Qt.ItemFlag.ItemIsEditable

    disconnect_from_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=MYSQL_CONNECTION.name,
    )


def test_supported_table_discard_postgresql(
    qtbot: QtBot,
    main_window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
):
    """
    Verifica que al modificar aleatoriamente varias celdas de
    table_supported y seleccionar Discard se restauran los
    valores originales en PostgreSQL.
    """

    auto_accept_confirmation_dialog(
        monkeypatch=monkeypatch,
    )

    connect_to_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=POSTGRESQL_CONNECTION.name,
    )

    workspace = get_workspace(
        main_window=main_window,
        connection=POSTGRESQL_CONNECTION,
    )

    sql_editor_area = get_sql_editor_area(
        main_window=main_window,
        connection=POSTGRESQL_CONNECTION,
    )

    editor = create_new_editor(
        sql_editor_area=sql_editor_area,
    )

    assert editor is not None

    editor.setPlainText(
        "SELECT * FROM table_supported;",
    )

    sql_editor_area.toolbar.execute_query_button.click()

    results_view = workspace.results_view

    qtbot.waitUntil(
        lambda: results_view.table.model is not None,
        timeout=5000,
    )

    model = results_view.table.model

    assert model is not None

    assert model.result_set.columns == [
        "id",
        "boolean_value",
        "date_value",
        "datetime_value",
        "float_value",
        "integer_value",
        "numeric_value",
        "string_value",
        "time_value",
        "uuid_value",
    ]

    # === MODIFICAR CELDAS ALEATORIAS ===

    editable_indexes = [
        model.index(row, column)
        for row in range(model.rowCount())
        for column in range(model.columnCount())
        if model.flags(
            model.index(row, column),
        )
        & Qt.ItemFlag.ItemIsEditable
    ]

    selected_indexes = random.sample(
        editable_indexes,
        k=5,
    )

    original_values = {
        index: index.data(Qt.ItemDataRole.DisplayRole) for index in selected_indexes
    }

    for index in selected_indexes:

        model.setData(
            index,
            f"Modified {random.randint(1000, 9999)}",
            Qt.ItemDataRole.EditRole,
        )

    # === COMPROBAR MODIFICACIONES ===

    for index, original_value in original_values.items():

        assert (
            index.data(
                Qt.ItemDataRole.DisplayRole,
            )
            != original_value
        )

    assert results_view.save_button.isEnabled()
    assert results_view.discard_button.isEnabled()

    # === DESCARTAR CAMBIOS ===

    results_view.discard_button.click()

    # === COMPROBAR RESTAURACIÓN ===

    for index, original_value in original_values.items():

        assert (
            index.data(
                Qt.ItemDataRole.DisplayRole,
            )
            == original_value
        )

    assert not results_view.save_button.isEnabled()
    assert not results_view.discard_button.isEnabled()

    disconnect_from_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=POSTGRESQL_CONNECTION.name,
    )


def test_supported_table_discard_mysql(
    qtbot: QtBot,
    main_window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
):
    """
    Verifica que al modificar aleatoriamente varias celdas de
    table_supported y seleccionar Discard se restauran los
    valores originales en MySQL.
    """

    auto_accept_confirmation_dialog(
        monkeypatch=monkeypatch,
    )

    connect_to_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=MYSQL_CONNECTION.name,
    )

    workspace = get_workspace(
        main_window=main_window,
        connection=MYSQL_CONNECTION,
    )

    sql_editor_area = get_sql_editor_area(
        main_window=main_window,
        connection=MYSQL_CONNECTION,
    )

    editor = create_new_editor(
        sql_editor_area=sql_editor_area,
    )

    assert editor is not None

    editor.setPlainText(
        "SELECT * FROM table_supported;",
    )

    sql_editor_area.toolbar.execute_query_button.click()

    results_view = workspace.results_view

    qtbot.waitUntil(
        lambda: results_view.table.model is not None,
        timeout=5000,
    )

    model = results_view.table.model

    assert model is not None

    assert model.result_set.columns == [
        "id",
        "boolean_value",
        "date_value",
        "datetime_value",
        "float_value",
        "integer_value",
        "numeric_value",
        "string_value",
        "time_value",
        "uuid_value",
    ]

    # === MODIFICAR CELDAS ALEATORIAS ===

    editable_indexes = [
        model.index(row, column)
        for row in range(model.rowCount())
        for column in range(model.columnCount())
        if model.flags(
            model.index(row, column),
        )
        & Qt.ItemFlag.ItemIsEditable
    ]

    selected_indexes = random.sample(
        editable_indexes,
        k=5,
    )

    original_values = {
        index: index.data(Qt.ItemDataRole.DisplayRole) for index in selected_indexes
    }

    for index in selected_indexes:

        model.setData(
            index,
            f"Modified {random.randint(1000, 9999)}",
            Qt.ItemDataRole.EditRole,
        )

    # === COMPROBAR MODIFICACIONES ===

    for index, original_value in original_values.items():

        assert (
            index.data(
                Qt.ItemDataRole.DisplayRole,
            )
            != original_value
        )

    assert results_view.save_button.isEnabled()
    assert results_view.discard_button.isEnabled()

    # === DESCARTAR CAMBIOS ===

    results_view.discard_button.click()

    # === COMPROBAR RESTAURACIÓN ===

    for index, original_value in original_values.items():

        assert (
            index.data(
                Qt.ItemDataRole.DisplayRole,
            )
            == original_value
        )

    assert not results_view.save_button.isEnabled()
    assert not results_view.discard_button.isEnabled()

    disconnect_from_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=MYSQL_CONNECTION.name,
    )

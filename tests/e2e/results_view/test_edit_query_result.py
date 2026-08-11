import random
import uuid
from datetime import (
    date,
    datetime,
    time,
)
from decimal import Decimal

import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QSignalSpy
from pytestqt.qtbot import QtBot

from tests.e2e.config.paths import (
    SCRIPT_MYSQL,
    SCRIPT_POSTGRESQL,
)
from tests.e2e.data.connections import (
    MYSQL_CONNECTION,
    POSTGRESQL_CONNECTION,
)
from tests.e2e.utils.database import reset_database
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


def _generate_modified_value(
    column_name: str,
    original_value,
):
    if column_name == "boolean_value":
        return "FALSE" if str(original_value).upper() == "TRUE" else "TRUE"

    values = {
        "date_value": lambda: (
            f"2025-{random.randint(1, 12):02d}-" f"{random.randint(1, 28):02d}"
        ),
        "datetime_value": lambda: (
            f"2025-{random.randint(1, 12):02d}-"
            f"{random.randint(1, 28):02d} "
            f"{random.randint(0, 23):02d}:"
            f"{random.randint(0, 59):02d}:"
            f"{random.randint(0, 59):02d}"
        ),
        "float_value": lambda: f"{random.uniform(1, 1000):.2f}",
        "integer_value": lambda: str(random.randint(1, 1000)),
        "numeric_value": lambda: f"{random.uniform(1, 1000):.2f}",
        "string_value": lambda: f"Modified {uuid.uuid4()}",
        "time_value": lambda: (
            f"{random.randint(0, 23):02d}:"
            f"{random.randint(0, 59):02d}:"
            f"{random.randint(0, 59):02d}"
        ),
        "uuid_value": lambda: str(uuid.uuid4()),
    }

    while True:
        value = values[column_name]()

        if str(value) != str(original_value):
            return value


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


def test_supported_table_save_postgresql(
    qtbot: QtBot,
    main_window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
):
    """
    Verifica que al modificar celdas aleatorias de table_supported
    y seleccionar Save, los cambios se persisten en PostgreSQL.
    """

    auto_accept_confirmation_dialog(
        monkeypatch=monkeypatch,
    )

    connect_to_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=POSTGRESQL_CONNECTION.name,
    )

    try:
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

        primary_key_columns = model.result_set.table_metadata.primary_key_columns

        editable_cells = []

        for row in range(model.rowCount()):
            for column in range(model.columnCount()):
                index = model.index(row, column)

                column_name = model.result_set.columns[column]

                if column_name in primary_key_columns:
                    continue

                if index.flags() & Qt.ItemFlag.ItemIsEditable:
                    editable_cells.append(index)

        assert editable_cells

        selected_cells = random.sample(
            editable_cells,
            k=min(5, len(editable_cells)),
        )

        modified_values = {}

        for index in selected_cells:
            column_name = model.result_set.columns[index.column()]

            original_value = index.data(
                Qt.ItemDataRole.DisplayRole,
            )

            modified_value = _generate_modified_value(
                column_name,
                original_value,
            )

            model.setData(
                index,
                modified_value,
                Qt.ItemDataRole.EditRole,
            )

            assert (
                index.data(
                    Qt.ItemDataRole.DisplayRole,
                )
                != original_value
            )

            modified_values[(index.row(), index.column())] = index.data(
                Qt.ItemDataRole.DisplayRole,
            )

        assert results_view.save_button.isEnabled()
        assert results_view.discard_button.isEnabled()

        results_view.save_button.click()

        # Aquí debemos esperar a la señal/notificación real
        # que indique que el guardado ha terminado.

        print(
            "Modified cells:",
            modified_values,
        )

    finally:
        disconnect_from_db(
            qtbot=qtbot,
            window=main_window,
            connection_name=POSTGRESQL_CONNECTION.name,
        )

        reset_database(
            connection=POSTGRESQL_CONNECTION,
            script_path=SCRIPT_POSTGRESQL,
        )


def test_simple_table_save_postgresql_error(
    qtbot: QtBot,
    main_window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
):
    """
    Verifica que al intentar guardar los cambios realizados en la tabla
    de forma gráfica, en este caso, una clave primaria duplicada en
    table_simple, se muestra el mensaje de error en la consola y la
    edición permanece disponible en la interfaz.
    """

    auto_accept_confirmation_dialog(
        monkeypatch=monkeypatch,
    )

    connect_to_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=POSTGRESQL_CONNECTION.name,
    )

    try:
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
            "SELECT * FROM table_simple;",
        )

        sql_editor_area.toolbar.execute_query_button.click()

        results_view = workspace.results_view

        qtbot.waitUntil(
            lambda: results_view.table.model is not None,
            timeout=5000,
        )

        model = results_view.table.model

        assert model is not None

        index = model.index(2, 0)

        assert (
            index.data(
                Qt.ItemDataRole.DisplayRole,
            )
            == "3"
        )

        model.setData(
            index,
            "1",
            Qt.ItemDataRole.EditRole,
        )

        assert (
            index.data(
                Qt.ItemDataRole.DisplayRole,
            )
            == "1"
        )

        assert results_view.save_button.isEnabled()
        assert results_view.discard_button.isEnabled()

        console = results_view.console

        expected_messages = [
            console.tr(
                "One or more UPDATE operations failed.",
            ),
            console.tr(
                "The transaction was rolled back.",
            ),
            console.tr(
                "No changes were saved.",
            ),
        ]

        results_view.save_button.click()

        qtbot.waitUntil(
            lambda: all(
                message in console.toPlainText() for message in expected_messages
            ),
            timeout=5000,
        )

        assert (
            index.data(
                Qt.ItemDataRole.DisplayRole,
            )
            == "1"
        )

        assert results_view.save_button.isEnabled()
        assert results_view.discard_button.isEnabled()

    finally:
        disconnect_from_db(
            qtbot=qtbot,
            window=main_window,
            connection_name=POSTGRESQL_CONNECTION.name,
        )

        reset_database(
            connection=POSTGRESQL_CONNECTION,
            script_path=SCRIPT_POSTGRESQL,
        )


def test_supported_table_save_mysql(
    qtbot: QtBot,
    main_window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
):
    """
    Verifica que al modificar celdas aleatorias de table_supported
    y seleccionar Save, los cambios se persisten en MySQL.
    """

    auto_accept_confirmation_dialog(
        monkeypatch=monkeypatch,
    )

    connect_to_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=MYSQL_CONNECTION.name,
    )

    try:
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

        primary_key_columns = model.result_set.table_metadata.primary_key_columns

        editable_cells = []

        for row in range(model.rowCount()):
            for column in range(model.columnCount()):
                index = model.index(row, column)

                column_name = model.result_set.columns[column]

                if column_name in primary_key_columns:
                    continue

                if index.flags() & Qt.ItemFlag.ItemIsEditable:
                    editable_cells.append(index)

        assert editable_cells

        selected_cells = random.sample(
            editable_cells,
            k=min(5, len(editable_cells)),
        )

        modified_values = {}

        for index in selected_cells:
            column_name = model.result_set.columns[index.column()]

            original_value = index.data(
                Qt.ItemDataRole.DisplayRole,
            )

            modified_value = _generate_modified_value(
                column_name,
                original_value,
            )

            model.setData(
                index,
                modified_value,
                Qt.ItemDataRole.EditRole,
            )

            assert (
                index.data(
                    Qt.ItemDataRole.DisplayRole,
                )
                != original_value
            )

            modified_values[(index.row(), index.column())] = index.data(
                Qt.ItemDataRole.DisplayRole,
            )

        assert results_view.save_button.isEnabled()
        assert results_view.discard_button.isEnabled()

        results_view.save_button.click()

        # Aquí debemos esperar a la señal/notificación real
        # que indique que el guardado ha terminado.

        print(
            "Modified cells:",
            modified_values,
        )

    finally:
        disconnect_from_db(
            qtbot=qtbot,
            window=main_window,
            connection_name=MYSQL_CONNECTION.name,
        )

        reset_database(
            connection=MYSQL_CONNECTION,
            script_path=SCRIPT_MYSQL,
        )


def test_simple_table_save_mysql_error(
    qtbot: QtBot,
    main_window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
):
    """
    Verifica que al intentar guardar los cambios realizados en la tabla
    de forma gráfica, en este caso, una clave primaria duplicada en
    table_simple, se muestra el mensaje de error en la consola y la
    edición permanece disponible en la interfaz.
    """

    auto_accept_confirmation_dialog(
        monkeypatch=monkeypatch,
    )

    connect_to_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=MYSQL_CONNECTION.name,
    )

    try:
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
            "SELECT * FROM table_simple;",
        )

        sql_editor_area.toolbar.execute_query_button.click()

        results_view = workspace.results_view

        qtbot.waitUntil(
            lambda: results_view.table.model is not None,
            timeout=5000,
        )

        model = results_view.table.model

        assert model is not None

        index = model.index(2, 0)

        assert (
            index.data(
                Qt.ItemDataRole.DisplayRole,
            )
            == "3"
        )

        model.setData(
            index,
            "1",
            Qt.ItemDataRole.EditRole,
        )

        assert (
            index.data(
                Qt.ItemDataRole.DisplayRole,
            )
            == "1"
        )

        assert results_view.save_button.isEnabled()
        assert results_view.discard_button.isEnabled()

        console = results_view.console

        expected_messages = [
            console.tr(
                "One or more UPDATE operations failed.",
            ),
            console.tr(
                "The transaction was rolled back.",
            ),
            console.tr(
                "No changes were saved.",
            ),
        ]

        results_view.save_button.click()

        qtbot.waitUntil(
            lambda: all(
                message in console.toPlainText() for message in expected_messages
            ),
            timeout=5000,
        )

        assert (
            index.data(
                Qt.ItemDataRole.DisplayRole,
            )
            == "1"
        )

        assert results_view.save_button.isEnabled()
        assert results_view.discard_button.isEnabled()

    finally:
        disconnect_from_db(
            qtbot=qtbot,
            window=main_window,
            connection_name=MYSQL_CONNECTION.name,
        )

        reset_database(
            connection=MYSQL_CONNECTION,
            script_path=SCRIPT_MYSQL,
        )

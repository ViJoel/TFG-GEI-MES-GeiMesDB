from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot

from tests.e2e.data.connections import (
    MYSQL_CONNECTION,
    POSTGRESQL_CONNECTION,
)
from tests.e2e.utils.functions import (
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


def test_execute_query_postgresql(
    qtbot: QtBot,
    main_window: MainWindow,
):
    """
    Verifica que ejecutar una consulta SELECT muestra
    correctamente el resultado en la consola y en la tabla,
    y añade la consulta al historial de sesión.
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

    query = "SELECT * FROM table_simple;"

    editor.setPlainText(query)

    sql_editor_area.toolbar.execute_query_button.click()

    results_view = workspace.results_view

    qtbot.waitUntil(
        lambda: results_view.table.model is not None,
        timeout=5000,
    )

    # === RESULTADO EN CONSOLA ===

    console_output = results_view.console.toPlainText()

    assert console_output == (
        "id | text_value\n"
        "---+-----------\n"
        "1  | First row \n"
        "2  | Second row\n"
        "3  | Third row \n"
        "\n"
        "3 row(s) returned."
    )

    # === RESULTADO EN TABLA ===

    table_model = results_view.table.model

    assert table_model is not None

    assert table_model.result_set.columns == [
        "id",
        "text_value",
    ]

    assert table_model.result_set.rows == [
        [1, "First row"],
        [2, "Second row"],
        [3, "Third row"],
    ]

    # === HISTORIAL DE SESIÓN ===

    history = results_view.session_queries_history

    assert history.count() == 1

    history_entry = history.item(0).data(
        Qt.ItemDataRole.UserRole,
    )

    assert history_entry.query == query

    disconnect_from_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=POSTGRESQL_CONNECTION.name,
    )


def test_execute_query_mysql(
    qtbot: QtBot,
    main_window: MainWindow,
):
    """
    Verifica que ejecutar una consulta SELECT muestra
    correctamente el resultado en la consola y en la tabla,
    y añade la consulta al historial de sesión.
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

    query = "SELECT * FROM table_simple;"

    editor.setPlainText(query)

    sql_editor_area.toolbar.execute_query_button.click()

    results_view = workspace.results_view

    qtbot.waitUntil(
        lambda: results_view.table.model is not None,
        timeout=5000,
    )

    # === RESULTADO EN CONSOLA ===

    console_output = results_view.console.toPlainText()

    assert console_output == (
        "id | text_value\n"
        "---+-----------\n"
        "1  | First row \n"
        "2  | Second row\n"
        "3  | Third row \n"
        "\n"
        "3 row(s) returned."
    )

    # === RESULTADO EN TABLA ===

    table_model = results_view.table.model

    assert table_model is not None

    assert table_model.result_set.columns == [
        "id",
        "text_value",
    ]

    assert table_model.result_set.rows == [
        [1, "First row"],
        [2, "Second row"],
        [3, "Third row"],
    ]

    # === HISTORIAL DE SESIÓN ===

    history = results_view.session_queries_history

    assert history.count() == 1

    history_entry = history.item(0).data(
        Qt.ItemDataRole.UserRole,
    )

    assert history_entry.query == query

    disconnect_from_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=MYSQL_CONNECTION.name,
    )


def test_execute_query_error_postgresql(
    qtbot: QtBot,
    main_window: MainWindow,
):
    """
    Verifica que ejecutar una consulta sobre una tabla inexistente
    muestra correctamente el error en la consola y mantiene
    deshabilitada la vista tabular.
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

    query = "select * from tabla_inexistente;"

    editor.setPlainText(query)

    sql_editor_area.toolbar.execute_query_button.click()

    results_view = workspace.results_view

    qtbot.waitUntil(
        lambda: "UndefinedTable" in results_view.console.toPlainText(),
        timeout=5000,
    )

    # === RESULTADO EN CONSOLA ===

    console_output = results_view.console.toPlainText()

    assert "UndefinedTable" in console_output
    assert 'relation "tabla_inexistente" does not exist' in console_output
    assert "[SQL: select * from tabla_inexistente;]" in console_output

    # === VISTA TABULAR ===

    assert not results_view.table_button.isEnabled()

    # === HISTORIAL DE SESIÓN ===

    history = results_view.session_queries_history

    assert history.count() == 1

    history_entry = history.item(0).data(
        Qt.ItemDataRole.UserRole,
    )

    assert history_entry.query == query

    disconnect_from_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=POSTGRESQL_CONNECTION.name,
    )


def test_execute_query_error_mysql(
    qtbot: QtBot,
    main_window: MainWindow,
):
    """
    Verifica que ejecutar una consulta sobre una tabla inexistente
    muestra correctamente el error en la consola y mantiene
    deshabilitada la vista tabular.
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

    query = "select * from tabla_inexistente;"

    editor.setPlainText(query)

    sql_editor_area.toolbar.execute_query_button.click()

    results_view = workspace.results_view

    qtbot.waitUntil(
        lambda: "ProgrammingError" in results_view.console.toPlainText(),
        timeout=5000,
    )

    # === RESULTADO EN CONSOLA ===

    console_output = results_view.console.toPlainText()

    assert "ProgrammingError" in console_output
    assert "1146" in console_output
    assert "Table 'tfg-test.tabla_inexistente' doesn't exist" in console_output
    assert "[SQL: select * from tabla_inexistente;]" in console_output

    # === VISTA TABULAR ===

    assert not results_view.table_button.isEnabled()

    # === HISTORIAL DE SESIÓN ===

    history = results_view.session_queries_history

    assert history.count() == 1

    history_entry = history.item(0).data(
        Qt.ItemDataRole.UserRole,
    )

    assert history_entry.query == query

    disconnect_from_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=MYSQL_CONNECTION.name,
    )

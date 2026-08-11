from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot

from tests.e2e.data.connections import POSTGRESQL_CONNECTION
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


def test_execute_selected_query(
    qtbot: QtBot,
    main_window: MainWindow,
):
    """
    Verifica que ejecutar una única consulta seleccionada
    muestra correctamente su resultado.
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

    query = "select * from table_simple;"

    editor.setPlainText(query)

    # Seleccionar toda la consulta.
    editor.selectAll()

    sql_editor_area.toolbar.execute_selection_button.click()

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


def test_execute_selected_script(
    qtbot: QtBot,
    main_window: MainWindow,
):
    """
    Verifica que ejecutar varias consultas seleccionadas
    las ejecuta como un script y no ejecuta las consultas
    que quedan fuera de la selección.
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

    script = (
        "select * from table_simple;\n\n"
        "select * from tabla_inexistente;\n\n"
        "select * from table_simple;"
    )

    editor.setPlainText(script)

    # Seleccionamos únicamente las dos primeras consultas.
    cursor = editor.textCursor()

    start = script.index("select * from table_simple;")
    end = script.index("select * from table_simple;", start + 1)

    cursor.setPosition(start)
    cursor.setPosition(
        end,
        cursor.MoveMode.KeepAnchor,
    )

    editor.setTextCursor(cursor)

    sql_editor_area.toolbar.execute_selection_button.click()

    results_view = workspace.results_view

    qtbot.waitUntil(
        lambda: "tabla_inexistente" in results_view.console.toPlainText(),
        timeout=5000,
    )

    # === RESULTADO EN CONSOLA ===

    console_output = results_view.console.toPlainText()

    assert console_output == (
        "select * from table_simple;\n\n"
        "--------------------------------------------------------------------------------\n\n"
        "select * from tabla_inexistente;\n\n"
        "Error: (psycopg.errors.UndefinedTable) "
        'relation "tabla_inexistente" does not exist\n'
        "LINE 1: select * from tabla_inexistente;\n"
        "                      ^\n"
        "[SQL: select * from tabla_inexistente;]\n"
        "(Background on this error at: "
        "https://sqlalche.me/e/20/f405)\n\n"
    )

    # === VISTA TABULAR ===

    assert not results_view.table_button.isEnabled()

    # === HISTORIAL DE SESIÓN ===

    history = results_view.session_queries_history

    assert history.count() == 2

    first_history_entry = history.item(0).data(
        Qt.ItemDataRole.UserRole,
    )

    second_history_entry = history.item(1).data(
        Qt.ItemDataRole.UserRole,
    )

    assert first_history_entry.query == "select * from table_simple;"

    assert second_history_entry.query == "select * from tabla_inexistente;"

    # La tercera consulta no estaba seleccionada.
    assert history.count() == 2

    disconnect_from_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=POSTGRESQL_CONNECTION.name,
    )

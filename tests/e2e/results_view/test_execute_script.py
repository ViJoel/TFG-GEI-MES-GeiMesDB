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


def test_execute_script_postgresql(
    qtbot: QtBot,
    main_window: MainWindow,
):
    """
    Verifica que ejecutar un script con una consulta válida
    y otra errónea muestra correctamente el resultado de
    ambas sentencias en la consola y mantiene deshabilitada
    la vista tabular.
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

    script = "select * from table_simple;\n\n" "select * from tabla_inexistente;"

    editor.setPlainText(script)

    sql_editor_area.toolbar.execute_script_button.click()

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

    disconnect_from_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=POSTGRESQL_CONNECTION.name,
    )


def test_execute_script_mysql(
    qtbot: QtBot,
    main_window: MainWindow,
):
    """
    Verifica que ejecutar un script con una consulta válida
    y otra errónea muestra correctamente el resultado de
    ambas sentencias en la consola y mantiene deshabilitada
    la vista tabular.
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

    script = "select * from table_simple;\n\n" "select * from tabla_inexistente;"

    editor.setPlainText(script)

    sql_editor_area.toolbar.execute_script_button.click()

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
        "Error: (pymysql.err.ProgrammingError) "
        "(1146, \"Table 'tfg-test.tabla_inexistente' doesn't exist\")\n"
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

    disconnect_from_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=MYSQL_CONNECTION.name,
    )

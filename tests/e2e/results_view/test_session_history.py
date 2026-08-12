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


def test_session_queries_history_postgresql(
    qtbot: QtBot,
    main_window: MainWindow,
):
    """
    Verifica que una consulta ejecutada se almacena en el
    historial de sesión y que al hacer doble clic sobre ella
    se recupera en el editor.
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

    # === HISTORIAL DE SESIÓN ===

    history = results_view.session_queries_history

    assert history.count() == 1

    item = history.item(0)

    history_item = history.itemWidget(item)

    assert history_item is not None

    # === LIMPIAR EDITOR ===

    editor.clear()

    assert editor.toPlainText() == ""

    # === RECUPERAR CONSULTA ===

    qtbot.mouseDClick(
        history_item,
        Qt.MouseButton.LeftButton,
    )

    assert editor.toPlainText() == query

    disconnect_from_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=POSTGRESQL_CONNECTION.name,
    )


def test_session_queries_history_mysql(
    qtbot: QtBot,
    main_window: MainWindow,
):
    """
    Verifica que una consulta ejecutada se almacena en el
    historial de sesión y que al hacer doble clic sobre ella
    se recupera en el editor.
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

    # === HISTORIAL DE SESIÓN ===

    history = results_view.session_queries_history

    assert history.count() == 1

    item = history.item(0)

    history_item = history.itemWidget(item)

    assert history_item is not None

    # === LIMPIAR EDITOR ===

    editor.clear()

    assert editor.toPlainText() == ""

    # === RECUPERAR CONSULTA ===

    qtbot.mouseDClick(
        history_item,
        Qt.MouseButton.LeftButton,
    )

    assert editor.toPlainText() == query

    disconnect_from_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=MYSQL_CONNECTION.name,
    )

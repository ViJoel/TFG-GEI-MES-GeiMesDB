import pytest
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


@pytest.mark.parametrize(
    "connection",
    [
        POSTGRESQL_CONNECTION,
        MYSQL_CONNECTION,
    ],
    ids=[
        "postgresql",
        "mysql",
    ],
)
def test_session_queries_history(
    qtbot: QtBot,
    main_window: MainWindow,
    connection,
):
    """
    Verifica que una consulta ejecutada se almacena en el
    historial de sesión y que al hacer doble clic sobre ella
    se recupera en el editor.
    """

    connect_to_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=connection.name,
    )

    workspace = get_workspace(
        main_window=main_window,
        connection=connection,
    )

    sql_editor_area = get_sql_editor_area(
        main_window=main_window,
        connection=connection,
    )

    editor = create_new_editor(
        sql_editor_area=sql_editor_area,
    )

    assert editor is not None

    query_without_semicolon = "SELECT * FROM table_simple"
    query_with_semicolon = f"{query_without_semicolon};"

    editor.setPlainText(query_with_semicolon)

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

    entry = item.data(
        Qt.ItemDataRole.UserRole,
    )

    assert entry.query == query_without_semicolon

    # === LIMPIAR EDITOR ===

    editor.clear()

    assert editor.toPlainText() == ""

    # === RECUPERAR CONSULTA ===

    qtbot.mouseDClick(
        history_item,
        Qt.MouseButton.LeftButton,
    )

    assert editor.toPlainText() == query_without_semicolon

    disconnect_from_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=connection.name,
    )

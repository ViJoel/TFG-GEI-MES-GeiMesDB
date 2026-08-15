from pathlib import Path

import pytest
from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot

from entities.connection import Connection
from entities.driver import Driver
from entities.message_type import MessageType
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
    connect_to_db,
    create_new_editor,
    disconnect_from_db,
    get_sql_editor_area,
    get_workspace,
)
from ui.app.app_context import AppContext
from ui.app.main_window import MainWindow
from ui.widgets.workspace.navigation_tree.tree_node_type import TreeNodeType

# =============================================================================
# VARIABLES
# =============================================================================

CREATE_TABLE_SQL = (
    "CREATE TABLE table_e2e_refresh ("
    "id INTEGER PRIMARY KEY, "
    "name VARCHAR(100) NOT NULL"
    ");"
)

INITIAL_TABLES = {
    "table_complex",
    "table_constraints_child",
    "table_constraints_parent",
    "table_simple",
    "table_supported",
}


# =============================================================================
# FUNCTIONS
# =============================================================================


def get_tree_item(
    item,
    text: str,
):
    """
    Busca recursivamente un item por su texto.
    """

    if item.text() == text:
        return item

    for row in range(item.rowCount()):

        child = item.child(row)

        if child is None:
            continue

        result = get_tree_item(
            item=child,
            text=text,
        )

        if result is not None:
            return result

    return None


def get_tables_folder(
    navigation_tree,
):
    """
    Obtiene el nodo raíz que contiene las tablas.
    """

    model = navigation_tree.model

    for row in range(model.rowCount()):

        item = model.item(row)

        if item is None:
            continue

        data = item.data(
            Qt.ItemDataRole.UserRole,
        )

        if data["type"] == TreeNodeType.TABLES_FOLDER:
            return item

    raise AssertionError(
        "Tables folder not found in navigation tree.",
    )


def get_child_by_type(
    item,
    node_type: TreeNodeType,
):
    """
    Obtiene el primer hijo que tenga el tipo indicado.
    """

    for row in range(item.rowCount()):

        child = item.child(row)

        if child is None:
            continue

        data = child.data(
            Qt.ItemDataRole.UserRole,
        )

        if data["type"] == node_type:
            return child

    return None


def get_child_names(
    item,
) -> set[str]:
    """
    Obtiene los nombres de los hijos directos de un item.

    Las columnas tienen el formato:

        <nombre> : <TIPO>

    Por tanto, para las columnas únicamente se conserva
    la parte correspondiente al nombre.
    """

    names = set()

    for row in range(item.rowCount()):

        child = item.child(row)

        if child is None:
            continue

        name = child.text().split(
            " : ",
            maxsplit=1,
        )[0]

        names.add(name)

    return names


def get_constraint_types(
    constraints_folder,
) -> set[str]:
    """
    Obtiene los tipos de restricciones mostradas dentro
    del nodo Constraints.
    """

    constraint_types = set()

    for row in range(constraints_folder.rowCount()):

        constraint = constraints_folder.child(row)

        if constraint is None:
            continue

        constraint_data = constraint.data(
            Qt.ItemDataRole.UserRole,
        )

        constraint_types.add(
            constraint_data["data"]["type"],
        )

    return constraint_types


def assert_table_structure(
    navigation_tree,
    table_name: str,
    expected_columns: set[str],
    expected_constraint_types: set[str],
) -> None:
    """
    Comprueba la estructura de una tabla del árbol.

    No comprueba iconos ni ningún otro detalle visual.

    La clave primaria no se comprueba dentro de Constraints,
    ya que la aplicación la representa mediante el icono de
    la columna correspondiente.
    """

    tables_folder = get_tables_folder(
        navigation_tree=navigation_tree,
    )

    table = get_tree_item(
        item=tables_folder,
        text=table_name,
    )

    assert table is not None

    table_data = table.data(
        Qt.ItemDataRole.UserRole,
    )

    assert table_data["type"] == TreeNodeType.TABLE

    # -------------------------------------------------------------------------
    # COLUMNS
    # -------------------------------------------------------------------------

    columns_folder = get_child_by_type(
        item=table,
        node_type=TreeNodeType.COLUMNS_FOLDER,
    )

    assert columns_folder is not None

    actual_columns = get_child_names(
        item=columns_folder,
    )

    assert actual_columns == expected_columns

    # -------------------------------------------------------------------------
    # CONSTRAINTS
    # -------------------------------------------------------------------------

    constraints_folder = get_child_by_type(
        item=table,
        node_type=TreeNodeType.CONSTRAINTS_FOLDER,
    )

    if expected_constraint_types:

        assert constraints_folder is not None

        actual_constraint_types = get_constraint_types(
            constraints_folder=constraints_folder,
        )

        assert actual_constraint_types == expected_constraint_types

    else:

        # Las tablas sin UNIQUE, FOREIGN KEY ni CHECK
        # no deben mostrar el nodo Constraints.
        assert constraints_folder is None


def assert_initial_tree_structure(
    navigation_tree,
    connection: Connection,
) -> None:
    """
    Comprueba la estructura inicial del árbol de navegación.

    Las expectativas de constraints pueden variar según el
    motor de base de datos.
    """

    tables_folder = get_tables_folder(
        navigation_tree=navigation_tree,
    )

    assert (
        tables_folder.data(
            Qt.ItemDataRole.UserRole,
        )["type"]
        == TreeNodeType.TABLES_FOLDER
    )

    actual_tables = get_child_names(
        item=tables_folder,
    )

    assert actual_tables == INITIAL_TABLES

    # -------------------------------------------------------------------------
    # EXPECTATIVAS SEGÚN EL MOTOR
    # -------------------------------------------------------------------------

    if connection.driver.name == "POSTGRESQL":

        table_simple_constraints = {
            "PRIMARY_KEY",
        }

        table_supported_constraints = {
            "PRIMARY_KEY",
        }

        table_complex_constraints = {
            "PRIMARY_KEY",
        }

        table_constraints_parent_constraints = {
            "PRIMARY_KEY",
            "UNIQUE",
        }

        table_constraints_child_constraints = {
            "PRIMARY_KEY",
            "FOREIGN_KEY",
            "CHECK",
        }

    elif connection.driver.name == "MYSQL":

        table_simple_constraints = set()

        table_supported_constraints = set()

        table_complex_constraints = set()

        table_constraints_parent_constraints = {
            "UNIQUE",
        }

        table_constraints_child_constraints = {
            "FOREIGN_KEY",
            "CHECK",
        }

    else:

        raise AssertionError(
            f"Unsupported database driver: {connection.driver}",
        )

    # -------------------------------------------------------------------------
    # table_simple
    # -------------------------------------------------------------------------

    assert_table_structure(
        navigation_tree=navigation_tree,
        table_name="table_simple",
        expected_columns={
            "id",
            "text_value",
        },
        expected_constraint_types=table_simple_constraints,
    )

    # -------------------------------------------------------------------------
    # table_supported
    # -------------------------------------------------------------------------

    assert_table_structure(
        navigation_tree=navigation_tree,
        table_name="table_supported",
        expected_columns={
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
        },
        expected_constraint_types=table_supported_constraints,
    )

    # -------------------------------------------------------------------------
    # table_complex
    # -------------------------------------------------------------------------

    assert_table_structure(
        navigation_tree=navigation_tree,
        table_name="table_complex",
        expected_columns={
            "id",
            "json_value",
            "array_value",
            "binary_value",
        },
        expected_constraint_types=table_complex_constraints,
    )

    # -------------------------------------------------------------------------
    # table_constraints_parent
    # -------------------------------------------------------------------------

    assert_table_structure(
        navigation_tree=navigation_tree,
        table_name="table_constraints_parent",
        expected_columns={
            "id",
            "name",
            "code",
        },
        expected_constraint_types=table_constraints_parent_constraints,
    )

    # -------------------------------------------------------------------------
    # table_constraints_child
    # -------------------------------------------------------------------------

    assert_table_structure(
        navigation_tree=navigation_tree,
        table_name="table_constraints_child",
        expected_columns={
            "id",
            "parent_id",
            "value",
        },
        expected_constraint_types=table_constraints_child_constraints,
    )


# =============================================================================
# TESTS
# =============================================================================


@pytest.mark.parametrize(
    "connection, script_path",
    [
        (
            POSTGRESQL_CONNECTION,
            SCRIPT_POSTGRESQL,
        ),
        (
            MYSQL_CONNECTION,
            SCRIPT_MYSQL,
        ),
    ],
)
def test_navigation_tree_initial_structure(
    qtbot: QtBot,
    main_window: MainWindow,
    connection: Connection,
    script_path: Path,
):
    """
    Verifica que el árbol de navegación muestra correctamente
    la estructura inicial de la base de datos.
    """

    reset_database(
        connection=connection,
        script_path=script_path,
    )

    connect_to_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=connection.name,
    )

    workspace = get_workspace(
        main_window=main_window,
        connection=connection,
    )

    navigation_tree = workspace.navigation_tree

    qtbot.waitUntil(
        lambda: (
            navigation_tree.model.rowCount() > 0
            and navigation_tree.model.item(0) is not None
            and navigation_tree.model.item(0).data(
                Qt.ItemDataRole.UserRole,
            )["type"]
            == TreeNodeType.TABLES_FOLDER
        ),
        timeout=5000,
    )

    assert_initial_tree_structure(
        navigation_tree=navigation_tree,
        connection=connection,
    )

    disconnect_from_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=connection.name,
    )


@pytest.mark.parametrize(
    "connection, script_path",
    [
        (
            POSTGRESQL_CONNECTION,
            SCRIPT_POSTGRESQL,
        ),
        (
            MYSQL_CONNECTION,
            SCRIPT_MYSQL,
        ),
    ],
)
def test_navigation_tree_refresh_after_create_table(
    qtbot: QtBot,
    main_window: MainWindow,
    connection: Connection,
    script_path: Path,
):
    """
    Verifica que el árbol de navegación se actualiza después
    de crear una nueva tabla y refrescar el árbol.
    """

    reset_database(
        connection=connection,
        script_path=script_path,
    )

    connect_to_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=connection.name,
    )

    workspace = get_workspace(
        main_window=main_window,
        connection=connection,
    )

    navigation_tree = workspace.navigation_tree

    qtbot.waitUntil(
        lambda: (
            navigation_tree.model.rowCount() > 0
            and navigation_tree.model.item(0) is not None
            and navigation_tree.model.item(0).data(
                Qt.ItemDataRole.UserRole,
            )["type"]
            == TreeNodeType.TABLES_FOLDER
        ),
        timeout=5000,
    )

    assert_initial_tree_structure(
        navigation_tree=navigation_tree,
        connection=connection,
    )

    # -------------------------------------------------------------------------
    # CREATE TABLE
    # -------------------------------------------------------------------------

    sql_editor_area = get_sql_editor_area(
        main_window=main_window,
        connection=connection,
    )

    editor = create_new_editor(
        sql_editor_area=sql_editor_area,
    )

    assert editor is not None

    editor.setPlainText(
        CREATE_TABLE_SQL,
    )

    sql_editor_area.toolbar.execute_query_button.click()

    notifications = AppContext.notification_manager.notifications

    previous_count = len(notifications)

    qtbot.waitUntil(
        lambda: any(
            notification.message
            == main_window.tr(
                "SQL query executed.",
            )
            and notification.message_type is MessageType.SUCCESS
            for notification in notifications[previous_count:]
        ),
        timeout=5000,
    )

    # -------------------------------------------------------------------------
    # REFRESH
    # -------------------------------------------------------------------------

    navigation_tree.refresh()

    qtbot.waitUntil(
        lambda: (
            get_tree_item(
                item=get_tables_folder(
                    navigation_tree=navigation_tree,
                ),
                text="table_e2e_refresh",
            )
            is not None
        ),
        timeout=5000,
    )

    # -------------------------------------------------------------------------
    # VERIFY NEW TABLE
    # -------------------------------------------------------------------------

    if connection.driver is Driver.POSTGRESQL:
        expected_constraint_types = {
            "PRIMARY_KEY",
        }

    elif connection.driver is Driver.MYSQL:
        expected_constraint_types = set()

    else:
        raise AssertionError(
            f"Unsupported database driver: {connection.driver}",
        )

    assert_table_structure(
        navigation_tree=navigation_tree,
        table_name="table_e2e_refresh",
        expected_columns={
            "id",
            "name",
        },
        expected_constraint_types=expected_constraint_types,
    )

    disconnect_from_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=connection.name,
    )

    reset_database(
        connection=connection,
        script_path=script_path,
    )

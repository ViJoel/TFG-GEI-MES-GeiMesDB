from unittest.mock import patch

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem
from PySide6.QtWidgets import QWidget

from entities.driver import Driver
from ui.widgets.workspace.navigation_tree.navigation_tree_context_menu import (
    NavigationTreeContextMenu,
)
from ui.widgets.workspace.navigation_tree.tree_node_type import TreeNodeType

# =============================================================================
# FIXTURES
# =============================================================================


def _menu(
    qtbot,
    node_type=TreeNodeType.TABLE,
    driver=Driver.POSTGRESQL,
):
    parent_widget = QWidget()
    qtbot.addWidget(parent_widget)

    item = QStandardItem("users")

    item.setData(
        {
            "type": node_type,
            "data": {
                "name": "id",
                "type": "INTEGER",
                "table": "users",
                "columns": [
                    {"name": "id"},
                    {"name": "name"},
                ],
            },
        },
        Qt.UserRole,
    )

    parent_item = QStandardItem("users")
    parent_item.appendRow(item)

    with patch(
        "ui.widgets.workspace.navigation_tree.navigation_tree_context_menu.get_session_driver",
        return_value=driver,
    ):
        menu = NavigationTreeContextMenu(
            parent_widget,
            item,
            "connection",
        )

    qtbot.addWidget(menu)

    return menu


# =============================================================================
# TABLE
# =============================================================================


@pytest.mark.parametrize(
    ("driver", "expected"),
    [
        (Driver.POSTGRESQL, "information_schema.tables"),
        (Driver.MYSQL, "information_schema.tables"),
        (Driver.SQLITE, "sqlite_master"),
        (Driver.ORACLE, "user_tables"),
    ],
)
def test_generate_tables_metadata(
    qtbot,
    driver,
    expected,
):
    menu = _menu(
        qtbot=qtbot,
        node_type=TreeNodeType.TABLES_FOLDER,
        driver=driver,
    )

    assert expected in menu._generate_tables_metadata()


@pytest.mark.parametrize(
    ("driver", "expected"),
    [
        (Driver.POSTGRESQL, "information_schema.tables"),
        (Driver.MYSQL, "information_schema.tables"),
        (Driver.SQLITE, "sqlite_master"),
        (Driver.ORACLE, "user_tables"),
    ],
)
def test_generate_table_metadata(
    qtbot,
    driver,
    expected,
):
    menu = _menu(
        qtbot=qtbot,
        node_type=TreeNodeType.TABLE,
        driver=driver,
    )

    assert expected in menu._generate_table_metadata()


@pytest.mark.parametrize(
    (
        "helper",
        "expected_parts",
    ),
    [
        (
            "_generate_table_select",
            [
                "SELECT *",
                "FROM users",
            ],
        ),
        (
            "_generate_table_insert",
            [
                "INSERT INTO users",
                "id",
                "name",
                "VALUES",
            ],
        ),
        (
            "_generate_table_update",
            [
                "UPDATE users",
                "id = ?",
                "name = ?",
            ],
        ),
        (
            "_generate_table_delete",
            [
                "DELETE FROM users",
                "WHERE",
            ],
        ),
        (
            "_generate_table_alter",
            [
                "ALTER TABLE users",
            ],
        ),
        (
            "_generate_table_drop",
            [
                "DROP TABLE users",
            ],
        ),
    ],
)
def test_generate_table_helpers(
    qtbot,
    helper,
    expected_parts,
):
    menu = _menu(
        qtbot=qtbot,
        node_type=TreeNodeType.TABLE,
    )

    generate = getattr(menu, helper)

    sql_without_semicolon = generate(
        with_semicolon=False,
    )
    sql_with_semicolon = generate(
        with_semicolon=True,
    )

    for expected_part in expected_parts:
        assert expected_part in sql_without_semicolon
        assert expected_part in sql_with_semicolon

    assert not sql_without_semicolon.endswith(";")
    assert sql_with_semicolon.endswith(";")

    assert sql_with_semicolon == (sql_without_semicolon + ";")


@pytest.mark.parametrize(
    ("driver", "expected"),
    [
        (Driver.POSTGRESQL, "information_schema.columns"),
        (Driver.MYSQL, "information_schema.columns"),
        (Driver.SQLITE, "PRAGMA table_info"),
        (Driver.ORACLE, "user_tab_columns"),
    ],
)
def test_generate_table_columns(
    qtbot,
    driver,
    expected,
):
    menu = _menu(
        qtbot=qtbot,
        node_type=TreeNodeType.TABLE,
        driver=driver,
    )

    assert expected in menu._generate_table_columns()


# =============================================================================
# COLUMN
# =============================================================================


@pytest.mark.parametrize(
    ("driver", "expected"),
    [
        (Driver.POSTGRESQL, "information_schema.columns"),
        (Driver.MYSQL, "information_schema.columns"),
        (Driver.SQLITE, "PRAGMA table_info"),
        (Driver.ORACLE, "user_tab_columns"),
    ],
)
def test_generate_columns_metadata(
    qtbot,
    driver,
    expected,
):
    menu = _menu(
        qtbot=qtbot,
        node_type=TreeNodeType.COLUMNS_FOLDER,
        driver=driver,
    )

    assert expected in menu._generate_columns_metadata()


@pytest.mark.parametrize(
    (
        "helper",
        "expected_parts",
    ),
    [
        (
            "_generate_column_select",
            [
                "SELECT id",
                "FROM users",
            ],
        ),
        (
            "_generate_column_where",
            [
                "WHERE id =",
            ],
        ),
        (
            "_generate_column_data",
            [
                "SELECT id",
                "FROM users",
            ],
        ),
    ],
)
def test_generate_column_helpers(
    qtbot,
    helper,
    expected_parts,
):
    menu = _menu(
        qtbot=qtbot,
        node_type=TreeNodeType.COLUMN,
    )

    generate = getattr(menu, helper)

    sql_without_semicolon = generate(
        with_semicolon=False,
    )
    sql_with_semicolon = generate(
        with_semicolon=True,
    )

    for expected_part in expected_parts:
        assert expected_part in sql_without_semicolon
        assert expected_part in sql_with_semicolon

    assert not sql_without_semicolon.endswith(";")
    assert sql_with_semicolon.endswith(";")

    assert sql_with_semicolon == (sql_without_semicolon + ";")


@pytest.mark.parametrize(
    ("driver", "expected"),
    [
        (Driver.POSTGRESQL, "information_schema.columns"),
        (Driver.MYSQL, "information_schema.columns"),
        (Driver.SQLITE, "PRAGMA table_info"),
        (Driver.ORACLE, "user_tab_columns"),
    ],
)
def test_generate_column_metadata(
    qtbot,
    driver,
    expected,
):
    menu = _menu(
        qtbot=qtbot,
        node_type=TreeNodeType.COLUMN,
        driver=driver,
    )

    assert expected in menu._generate_column_metadata()


# =============================================================================
# CONSTRAINT
# =============================================================================


@pytest.mark.parametrize(
    ("driver", "expected"),
    [
        (Driver.POSTGRESQL, "table_constraints"),
        (Driver.MYSQL, "table_constraints"),
        (Driver.SQLITE, "sqlite_master"),
        (Driver.ORACLE, "user_constraints"),
    ],
)
def test_generate_constraints_metadata(
    qtbot,
    driver,
    expected,
):
    menu = _menu(
        qtbot=qtbot,
        node_type=TreeNodeType.CONSTRAINTS_FOLDER,
        driver=driver,
    )

    assert expected in menu._generate_constraints_metadata()


@pytest.mark.parametrize(
    ("driver", "expected"),
    [
        (Driver.POSTGRESQL, "table_constraints"),
        (Driver.MYSQL, "table_constraints"),
        (Driver.SQLITE, "sqlite_master"),
        (Driver.ORACLE, "user_constraints"),
    ],
)
def test_generate_constraint_details(
    qtbot,
    driver,
    expected,
):
    menu = _menu(
        qtbot=qtbot,
        node_type=TreeNodeType.CONSTRAINT,
        driver=driver,
    )

    assert expected in menu._generate_constraint_details()


# =============================================================================
# INDEX
# =============================================================================


@pytest.mark.parametrize(
    ("driver", "expected"),
    [
        (Driver.POSTGRESQL, "pg_indexes"),
        (Driver.MYSQL, "statistics"),
        (Driver.SQLITE, "PRAGMA index_list"),
        (Driver.ORACLE, "user_indexes"),
    ],
)
def test_generate_indexes_metadata(
    qtbot,
    driver,
    expected,
):
    menu = _menu(
        qtbot=qtbot,
        node_type=TreeNodeType.INDEXES_FOLDER,
        driver=driver,
    )

    assert expected in menu._generate_indexes_metadata()


@pytest.mark.parametrize(
    ("driver", "expected"),
    [
        (Driver.POSTGRESQL, "pg_indexes"),
        (Driver.MYSQL, "statistics"),
        (Driver.SQLITE, "sqlite_master"),
        (Driver.ORACLE, "user_indexes"),
    ],
)
def test_generate_index_details(
    qtbot,
    driver,
    expected,
):
    menu = _menu(
        qtbot=qtbot,
        node_type=TreeNodeType.INDEX,
        driver=driver,
    )

    assert expected in menu._generate_index_details()


# =============================================================================
# VIEW
# =============================================================================


@pytest.mark.parametrize(
    ("driver", "expected"),
    [
        (Driver.POSTGRESQL, "information_schema.views"),
        (Driver.MYSQL, "information_schema.views"),
        (Driver.SQLITE, "sqlite_master"),
        (Driver.ORACLE, "user_views"),
    ],
)
def test_generate_views_metadata(
    qtbot,
    driver,
    expected,
):
    menu = _menu(
        qtbot=qtbot,
        node_type=TreeNodeType.VIEWS_FOLDER,
        driver=driver,
    )

    assert expected in menu._generate_views_metadata()


@pytest.mark.parametrize(
    ("driver", "expected"),
    [
        (Driver.POSTGRESQL, "information_schema.views"),
        (Driver.MYSQL, "information_schema.views"),
        (Driver.SQLITE, "sqlite_master"),
        (Driver.ORACLE, "user_views"),
    ],
)
def test_generate_view_metadata(
    qtbot,
    driver,
    expected,
):
    menu = _menu(
        qtbot=qtbot,
        node_type=TreeNodeType.VIEW,
        driver=driver,
    )

    assert expected in menu._generate_view_metadata()


@pytest.mark.parametrize(
    (
        "helper",
        "expected_parts",
    ),
    [
        (
            "_generate_view_select",
            [
                "SELECT *",
                "FROM users",
            ],
        ),
        (
            "_generate_view_data",
            [
                "SELECT *",
                "FROM users",
            ],
        ),
        (
            "_generate_view_drop",
            [
                "DROP VIEW users",
            ],
        ),
    ],
)
def test_generate_view_helpers(
    qtbot,
    helper,
    expected_parts,
):
    menu = _menu(
        qtbot=qtbot,
        node_type=TreeNodeType.VIEW,
    )

    generate = getattr(menu, helper)

    sql_without_semicolon = generate(
        with_semicolon=False,
    )
    sql_with_semicolon = generate(
        with_semicolon=True,
    )

    for expected_part in expected_parts:
        assert expected_part in sql_without_semicolon
        assert expected_part in sql_with_semicolon

    assert not sql_without_semicolon.endswith(";")
    assert sql_with_semicolon.endswith(";")

    assert sql_with_semicolon == (sql_without_semicolon + ";")


@pytest.mark.parametrize(
    ("driver", "expected"),
    [
        (Driver.POSTGRESQL, "information_schema.columns"),
        (Driver.MYSQL, "information_schema.columns"),
        (Driver.SQLITE, "PRAGMA table_info"),
        (Driver.ORACLE, "user_tab_columns"),
    ],
)
def test_generate_view_columns(
    qtbot,
    driver,
    expected,
):
    menu = _menu(
        qtbot=qtbot,
        node_type=TreeNodeType.VIEW,
        driver=driver,
    )

    assert expected in menu._generate_view_columns()


# =============================================================================
# INVALID DRIVER
# =============================================================================


@pytest.mark.parametrize(
    "helper",
    [
        "_generate_tables_metadata",
        "_generate_table_metadata",
        "_generate_table_columns",
        "_generate_columns_metadata",
        "_generate_column_metadata",
        "_generate_constraints_metadata",
        "_generate_constraint_details",
        "_generate_indexes_metadata",
        "_generate_index_details",
        "_generate_views_metadata",
        "_generate_view_metadata",
    ],
)
@pytest.mark.parametrize(
    ("with_semicolon", "expected"),
    [
        (False, ""),
        (True, ";"),
    ],
)
def test_generate_helpers_invalid_driver(
    qtbot,
    helper,
    with_semicolon,
    expected,
):
    menu = _menu(
        qtbot=qtbot,
    )

    menu.sgbd_driver = object()

    generate = getattr(menu, helper)

    assert (
        generate(
            with_semicolon=with_semicolon,
        )
        == expected
    )

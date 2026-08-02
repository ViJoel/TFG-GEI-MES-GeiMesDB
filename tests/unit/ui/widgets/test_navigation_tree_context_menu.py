from unittest.mock import (
    MagicMock,
    patch,
)

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
# TESTS
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
        driver=driver,
    )

    assert expected in menu._generate_tables_metadata()


def test_generate_table_select(
    qtbot,
):
    menu = _menu(
        qtbot=qtbot,
    )

    assert menu._generate_table_select() == ("SELECT *\n" "FROM users;")


def test_generate_table_insert(
    qtbot,
):
    menu = _menu(
        qtbot=qtbot,
    )

    sql = menu._generate_table_insert()

    assert "INSERT INTO users" in sql
    assert "id" in sql
    assert "name" in sql
    assert "VALUES" in sql


def test_generate_table_update(
    qtbot,
):
    menu = _menu(
        qtbot=qtbot,
    )

    sql = menu._generate_table_update()

    assert sql.startswith("UPDATE users")
    assert "id = ?" in sql
    assert "name = ?" in sql


def test_generate_table_delete(
    qtbot,
):
    menu = _menu(
        qtbot=qtbot,
    )

    assert menu._generate_table_delete() == ("DELETE FROM users\n" "WHERE ;")


def test_generate_table_alter(
    qtbot,
):
    menu = _menu(
        qtbot=qtbot,
    )

    assert menu._generate_table_alter() == ("ALTER TABLE users\n" "\n" ";")


def test_generate_table_drop(
    qtbot,
):
    menu = _menu(
        qtbot=qtbot,
    )

    assert menu._generate_table_drop() == "DROP TABLE users;"


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
    menu = _menu(qtbot=qtbot, driver=driver)

    assert expected in menu._generate_table_columns()


def test_generate_column_select(
    qtbot,
):
    menu = _menu(
        qtbot=qtbot,
    )

    assert menu._generate_column_select() == ("SELECT id\n" "FROM users;")


def test_generate_column_where(
    qtbot,
):
    menu = _menu(
        qtbot=qtbot,
    )

    assert menu._generate_column_where() == "WHERE id = "


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
        driver=driver,
    )

    assert expected in menu._generate_constraints_metadata()


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
        driver=driver,
    )

    assert expected in menu._generate_indexes_metadata()


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
        driver=driver,
    )

    assert expected in menu._generate_views_metadata()


def test_generate_view_drop(
    qtbot,
):
    menu = _menu(
        qtbot=qtbot,
    )

    assert menu._generate_view_drop() == "DROP VIEW users;"


def test_generate_view_select(
    qtbot,
):
    menu = _menu(
        qtbot=qtbot,
    )

    assert menu._generate_view_select() == ("SELECT *\n" "FROM users;")


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
        driver=driver,
    )

    assert expected in menu._generate_table_metadata()


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
        driver=driver,
    )

    assert expected in menu._generate_columns_metadata()


def test_generate_column_data(
    qtbot,
):
    menu = _menu(
        qtbot=qtbot,
    )

    assert menu._generate_column_data() == ("SELECT id\n" "FROM users;")


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
        driver=driver,
    )

    assert expected in menu._generate_column_metadata()


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
        driver=driver,
    )

    assert expected in menu._generate_constraint_details()


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
        driver=driver,
    )

    assert expected in menu._generate_index_details()


def test_generate_view_data(
    qtbot,
):
    menu = _menu(
        qtbot=qtbot,
    )

    assert menu._generate_view_data() == ("SELECT *\n" "FROM users;")


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
        driver=driver,
    )

    assert expected in menu._generate_view_metadata()


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
        driver=driver,
    )

    assert expected in menu._generate_view_columns()

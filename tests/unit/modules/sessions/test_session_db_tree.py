from unittest.mock import (
    MagicMock,
    patch,
)

from sqlalchemy.sql.sqltypes import (
    Integer,
    NullType,
)

from modules.sessions.db_tree import (
    _build_columns,
    _build_completion_data,
    _extract_all_views_metadata,
    _extract_columns,
    _extract_constraints,
    _extract_indexes,
    _extract_schema_metadata,
    _extract_single_view_metadata,
    _extract_table_metadata,
    get_db_tree,
)

# =============================================================================
# get_db_tree
# =============================================================================


def test_get_db_tree_returns_none_when_session_not_exists():
    with patch(
        "modules.sessions.db_tree.get_session",
        return_value=None,
    ):
        assert get_db_tree("connection") is None


def test_get_db_tree_returns_metadata():
    session = MagicMock()
    session.engine = MagicMock()

    expected = {
        "tables": {},
        "views": {},
    }

    with (
        patch(
            "modules.sessions.db_tree.get_session",
            return_value=session,
        ),
        patch(
            "modules.sessions.db_tree._extract_schema_metadata",
            return_value=expected,
        ),
    ):
        assert get_db_tree("connection") == expected


def test_get_db_tree_returns_metadata_and_updates_completion_data():
    session = MagicMock()
    session.engine = MagicMock()

    tree_data = {
        "tables": {},
        "views": {},
    }

    completion_data = {
        "tables": [],
        "views": [],
        "columns": [],
        "constraints": [],
        "indexes": [],
    }

    with (
        patch(
            "modules.sessions.db_tree.get_session",
            return_value=session,
        ),
        patch(
            "modules.sessions.db_tree._extract_schema_metadata",
            return_value=tree_data,
        ),
        patch(
            "modules.sessions.db_tree._build_completion_data",
            return_value=completion_data,
        ) as build_completion_data,
        patch(
            "modules.sessions.db_tree.SQL_SCHEMA_COMPLETION_DATA.update",
        ) as update_completion_data,
    ):
        result = get_db_tree("connection")

    assert result == tree_data

    build_completion_data.assert_called_once_with(tree_data)

    update_completion_data.assert_called_once_with(
        completion_data,
    )


def test_get_db_tree_returns_none_when_exception():
    session = MagicMock()
    session.engine = MagicMock()

    with (
        patch(
            "modules.sessions.db_tree.get_session",
            return_value=session,
        ),
        patch(
            "modules.sessions.db_tree._extract_schema_metadata",
            side_effect=Exception,
        ),
        patch(
            "modules.sessions.db_tree.SQL_SCHEMA_COMPLETION_DATA.update",
        ) as update_completion_data,
    ):
        assert get_db_tree("connection") is None

    update_completion_data.assert_not_called()


# =============================================================================
# _extract_schema_metadata
# =============================================================================


def test_extract_schema_metadata():
    inspector = MagicMock()

    inspector.get_table_names.return_value = [
        "users",
        "roles",
    ]

    with (
        patch(
            "modules.sessions.db_tree.inspect",
            return_value=inspector,
        ),
        patch(
            "modules.sessions.db_tree._extract_table_metadata",
            side_effect=[
                {"columns": []},
                {"columns": []},
            ],
        ),
        patch(
            "modules.sessions.db_tree._extract_all_views_metadata",
            return_value={"v_users": {}},
        ),
    ):
        result = _extract_schema_metadata(MagicMock())

    assert result == {
        "tables": {
            "users": {"columns": []},
            "roles": {"columns": []},
        },
        "views": {
            "v_users": {},
        },
    }


# =============================================================================
# _extract_table_metadata
# =============================================================================


def test_extract_table_metadata():
    inspector = MagicMock()

    inspector.get_pk_constraint.return_value = {
        "name": "pk_users",
        "constrained_columns": ["id"],
    }

    inspector.get_foreign_keys.return_value = [
        {
            "constrained_columns": ["role_id"],
        }
    ]

    inspector.get_unique_constraints.return_value = [
        {
            "column_names": ["email"],
        }
    ]

    with (
        patch(
            "modules.sessions.db_tree._extract_columns",
            return_value=["columns"],
        ) as columns_mock,
        patch(
            "modules.sessions.db_tree._extract_constraints",
            return_value=["constraints"],
        ) as constraints_mock,
        patch(
            "modules.sessions.db_tree._extract_indexes",
            return_value=["indexes"],
        ) as indexes_mock,
    ):
        result = _extract_table_metadata(
            inspector,
            "users",
        )

    columns_mock.assert_called_once()
    constraints_mock.assert_called_once()
    indexes_mock.assert_called_once()

    assert result == {
        "columns": ["columns"],
        "constraints": ["constraints"],
        "indexes": ["indexes"],
    }


# =============================================================================
# _build_columns
# =============================================================================


def test_build_columns():
    result = _build_columns(
        [
            {
                "name": "id",
                "type": Integer(),
                "nullable": False,
                "default": 1,
            }
        ],
        "users",
        {"id"},
        {"id"},
        {"id"},
    )

    assert result == [
        {
            "name": "id",
            "type": "INTEGER",
            "pk": True,
            "fk": True,
            "unique": True,
            "nullable": False,
            "default": "1",
        }
    ]


def test_build_columns_with_nulltype():
    result = _build_columns(
        [
            {
                "name": "data",
                "type": NullType(),
            }
        ],
        "users",
    )

    assert result[0]["type"] == "UNKNOWN TYPE"


def test_build_columns_without_default():
    result = _build_columns(
        [
            {
                "name": "name",
                "type": Integer(),
            }
        ],
        "users",
    )

    assert result[0]["default"] is None


# =============================================================================
# _extract_columns
# =============================================================================


def test_extract_columns():
    inspector = MagicMock()

    inspector.get_columns.return_value = [
        {
            "name": "id",
            "type": "INTEGER",
        }
    ]

    with patch(
        "modules.sessions.db_tree._build_columns",
        return_value=["column"],
    ) as build_mock:
        result = _extract_columns(
            inspector,
            "users",
            {"id"},
            set(),
            set(),
        )

    build_mock.assert_called_once_with(
        inspector.get_columns.return_value,
        "users",
        {"id"},
        set(),
        set(),
    )

    assert result == ["column"]


# =============================================================================
# _extract_constraints
# =============================================================================


def test_extract_constraints():
    inspector = MagicMock()

    inspector.get_unique_constraints.return_value = [
        {
            "name": "uq_email",
            "column_names": ["email"],
        }
    ]

    inspector.get_check_constraints.return_value = [
        {
            "name": "ck_age",
            "sqltext": "age > 0",
        }
    ]

    result = _extract_constraints(
        inspector,
        "users",
        {
            "name": "pk_users",
        },
        {"id"},
        [
            {
                "name": "fk_role",
                "constrained_columns": ["role_id"],
                "referred_table": "roles",
                "referred_columns": ["id"],
            }
        ],
    )

    assert result == [
        {
            "name": "pk_users",
            "type": "PRIMARY_KEY",
            "columns": ["id"],
        },
        {
            "name": "fk_role",
            "type": "FOREIGN_KEY",
            "columns": ["role_id"],
            "referred_table": "roles",
            "referred_columns": ["id"],
        },
        {
            "name": "uq_email",
            "type": "UNIQUE",
            "columns": ["email"],
        },
        {
            "name": "ck_age",
            "type": "CHECK",
            "sqltext": "age > 0",
        },
    ]


def test_extract_constraints_without_primary_key():
    inspector = MagicMock()

    inspector.get_unique_constraints.return_value = []
    inspector.get_check_constraints.return_value = []

    result = _extract_constraints(
        inspector,
        "users",
        {},
        set(),
        [],
    )

    assert result == []


def test_extract_constraints_builds_foreign_key_name():
    inspector = MagicMock()

    inspector.get_unique_constraints.return_value = []
    inspector.get_check_constraints.return_value = []

    result = _extract_constraints(
        inspector,
        "users",
        {},
        set(),
        [
            {
                "constrained_columns": ["role_id"],
                "referred_table": "roles",
                "referred_columns": ["id"],
            }
        ],
    )

    assert result == [
        {
            "name": "fk_users_roles",
            "type": "FOREIGN_KEY",
            "columns": ["role_id"],
            "referred_table": "roles",
            "referred_columns": ["id"],
        }
    ]


# =============================================================================
# _extract_indexes
# =============================================================================


def test_extract_indexes():
    inspector = MagicMock()

    inspector.get_indexes.return_value = [
        {
            "name": "idx_name",
            "column_names": ["name"],
            "unique": True,
        },
        {
            "name": "idx_email",
            "column_names": ["email"],
            "unique": False,
        },
    ]

    result = _extract_indexes(
        inspector,
        "users",
    )

    assert result == [
        {
            "name": "idx_name",
            "columns": ["name"],
            "unique": True,
        },
        {
            "name": "idx_email",
            "columns": ["email"],
            "unique": False,
        },
    ]


def test_extract_indexes_empty():
    inspector = MagicMock()

    inspector.get_indexes.return_value = []

    assert (
        _extract_indexes(
            inspector,
            "users",
        )
        == []
    )


# =============================================================================
# _extract_all_views_metadata
# =============================================================================


def test_extract_all_views_metadata():
    inspector = MagicMock()

    inspector.get_view_names.return_value = [
        "view1",
    ]

    inspector.get_materialized_view_names.return_value = [
        "mat_view",
    ]

    with patch(
        "modules.sessions.db_tree._extract_single_view_metadata",
        side_effect=[
            {"type": "view"},
            {"type": "mat"},
        ],
    ):
        result = _extract_all_views_metadata(inspector)

    assert result == {
        "view1": {"type": "view"},
        "mat_view": {"type": "mat"},
    }


def test_extract_all_views_metadata_without_standard_views():
    inspector = MagicMock()

    inspector.get_view_names.side_effect = NotImplementedError
    inspector.get_materialized_view_names.return_value = []

    assert _extract_all_views_metadata(inspector) == {}


def test_extract_all_views_metadata_without_materialized_views():
    inspector = MagicMock()

    inspector.get_view_names.return_value = ["view1"]
    inspector.get_materialized_view_names.side_effect = AttributeError

    with patch(
        "modules.sessions.db_tree._extract_single_view_metadata",
        return_value={},
    ):
        result = _extract_all_views_metadata(inspector)

    assert result == {
        "view1": {},
    }


# =============================================================================
# _extract_single_view_metadata
# =============================================================================


def test_extract_single_view_metadata():
    inspector = MagicMock()

    inspector.get_columns.return_value = [
        {
            "name": "id",
            "type": "INTEGER",
        }
    ]

    inspector.get_view_definition.return_value = "SELECT * FROM users"

    with (
        patch(
            "modules.sessions.db_tree._build_columns",
            return_value=["column"],
        ),
        patch(
            "modules.sessions.db_tree._extract_indexes",
            return_value=["index"],
        ),
    ):
        result = _extract_single_view_metadata(
            inspector,
            "users_view",
            True,
        )

    assert result == {
        "is_materialized": True,
        "definition": "SELECT * FROM users",
        "columns": ["column"],
        "indexes": ["index"],
    }


def test_extract_single_view_metadata_without_columns():
    inspector = MagicMock()

    inspector.get_columns.side_effect = NotImplementedError
    inspector.get_view_definition.return_value = "SELECT 1"

    result = _extract_single_view_metadata(
        inspector,
        "users_view",
        False,
    )

    assert result == {
        "is_materialized": False,
        "definition": "SELECT 1",
        "columns": [],
        "indexes": [],
    }


def test_extract_single_view_metadata_without_definition():
    inspector = MagicMock()

    inspector.get_columns.return_value = []

    inspector.get_view_definition.side_effect = AttributeError

    with patch(
        "modules.sessions.db_tree._build_columns",
        return_value=[],
    ):
        result = _extract_single_view_metadata(
            inspector,
            "users_view",
            False,
        )

    assert result == {
        "is_materialized": False,
        "definition": None,
        "columns": [],
        "indexes": [],
    }


def test_extract_single_view_metadata_materialized_without_indexes():
    inspector = MagicMock()

    inspector.get_columns.return_value = []
    inspector.get_view_definition.return_value = None

    with (
        patch(
            "modules.sessions.db_tree._build_columns",
            return_value=[],
        ),
        patch(
            "modules.sessions.db_tree._extract_indexes",
            side_effect=NotImplementedError,
        ),
    ):
        result = _extract_single_view_metadata(
            inspector,
            "users_view",
            True,
        )

    assert result == {
        "is_materialized": True,
        "definition": None,
        "columns": [],
        "indexes": [],
    }


def test_extract_single_view_metadata_not_materialized_does_not_read_indexes():
    inspector = MagicMock()

    inspector.get_columns.return_value = []
    inspector.get_view_definition.return_value = None

    with (
        patch(
            "modules.sessions.db_tree._build_columns",
            return_value=[],
        ),
        patch(
            "modules.sessions.db_tree._extract_indexes",
        ) as indexes_mock,
    ):
        _extract_single_view_metadata(
            inspector,
            "users_view",
            False,
        )

    indexes_mock.assert_not_called()


# =============================================================================
# _build_completion_data
# =============================================================================


def test_build_completion_data():
    tree_data = {
        "tables": {
            "users": {
                "columns": [
                    {"name": "id"},
                    {"name": "name"},
                ],
                "constraints": [
                    {"name": "pk_users"},
                    {"name": "uq_users_name"},
                ],
                "indexes": [
                    {"name": "ix_users_name"},
                ],
            },
        },
        "views": {
            "active_users": {
                "columns": [
                    {"name": "id"},
                    {"name": "name"},
                ],
                "indexes": [
                    {"name": "ix_active_users"},
                ],
            },
        },
    }

    assert _build_completion_data(tree_data) == {
        "tables": ["users"],
        "views": ["active_users"],
        "columns": ["id", "name"],
        "constraints": [
            "pk_users",
            "uq_users_name",
        ],
        "indexes": [
            "ix_active_users",
            "ix_users_name",
        ],
    }


def test_build_completion_data_removes_duplicates():
    tree_data = {
        "tables": {
            "users": {
                "columns": [
                    {"name": "id"},
                    {"name": "name"},
                ],
                "constraints": [
                    {"name": "pk_users"},
                    {"name": "pk_users"},
                    {"name": None},
                ],
                "indexes": [
                    {"name": "ix_users"},
                    {"name": "ix_users"},
                ],
            },
            "employees": {
                "columns": [
                    {"name": "id"},
                    {"name": "name"},
                ],
                "constraints": [
                    {"name": "pk_users"},
                ],
                "indexes": [
                    {"name": "ix_users"},
                ],
            },
        },
        "views": {
            "employees_view": {
                "columns": [
                    {"name": "id"},
                    {"name": "name"},
                ],
                "indexes": [
                    {"name": "ix_users"},
                ],
            },
        },
    }

    assert _build_completion_data(tree_data) == {
        "tables": [
            "employees",
            "users",
        ],
        "views": [
            "employees_view",
        ],
        "columns": [
            "id",
            "name",
        ],
        "constraints": [
            "pk_users",
        ],
        "indexes": [
            "ix_users",
        ],
    }


def test_build_completion_data_empty_tree():
    assert _build_completion_data(
        {
            "tables": {},
            "views": {},
        }
    ) == {
        "tables": [],
        "views": [],
        "columns": [],
        "constraints": [],
        "indexes": [],
    }

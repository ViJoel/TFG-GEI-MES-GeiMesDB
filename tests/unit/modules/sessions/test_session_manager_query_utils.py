from unittest.mock import MagicMock

import pytest

import modules.sessions.manager as manager
from entities.query_result import ResultSet

# =============================================================================
# is_editable_query
# =============================================================================


@pytest.mark.parametrize(
    "query",
    [
        "SELECT * FROM users",
        " select * from users ",
        "SELECT    *    FROM    users",
        "SELECT * FROM users;",
    ],
)
def test_is_editable_query_valid(query):
    """
    Debe aceptar consultas editables.
    """

    assert manager.is_editable_query(query)


@pytest.mark.parametrize(
    "query",
    [
        "SELECT id FROM users",
        "SELECT * FROM users WHERE id=1",
        "SELECT * FROM users JOIN roles ON ...",
        "SELECT DISTINCT * FROM users",
        "UPDATE users SET name='A'",
        "DELETE FROM users",
        "INSERT INTO users VALUES (1)",
        "WITH cte AS (...) SELECT * FROM cte",
    ],
)
def test_is_editable_query_invalid(query):
    """
    Debe rechazar consultas no editables.
    """

    assert not manager.is_editable_query(query)


# =============================================================================
# _infer_column_types
# =============================================================================


def test_infer_column_types():
    """
    Debe inferir correctamente los tipos.
    """

    result = manager._infer_column_types(
        columns=["id", "name", "active"],
        rows=[
            [1, "Alice", True],
            [2, "Bob", False],
        ],
    )

    assert result == [int, str, bool]


def test_infer_column_types_with_none():
    """
    Debe ignorar valores None.
    """

    result = manager._infer_column_types(
        columns=["id", "value"],
        rows=[
            [None, None],
            [1, "text"],
        ],
    )

    assert result == [int, str]


def test_infer_column_types_all_none():
    """
    Si toda una columna es None debe asumir str.
    """

    result = manager._infer_column_types(
        columns=["a", "b"],
        rows=[
            [None, None],
            [None, None],
        ],
    )

    assert result == [str, str]


# =============================================================================
# _format_result_set
# =============================================================================


def test_format_result_set():
    """
    Debe construir correctamente la tabla.
    """

    rs = ResultSet(
        columns=["id", "name"],
        rows=[
            [1, "Alice"],
            [20, "Bob"],
        ],
        columns_types=[int, str],
        table_name=None,
        primary_key_columns=[],
    )

    text = manager._format_result_set(rs)

    assert "id" in text
    assert "name" in text
    assert "Alice" in text
    assert "Bob" in text
    assert "-" in text


# =============================================================================
# _create_console_output
# =============================================================================


@pytest.mark.parametrize(
    "query,rowcount,expected",
    [
        ("INSERT INTO users VALUES (1)", 5, "5 row(s) inserted."),
        ("UPDATE users SET name='A'", 2, "2 row(s) updated."),
        ("DELETE FROM users", 8, "8 row(s) deleted."),
        ("CREATE TABLE users(id INT)", 0, "Query executed successfully."),
    ],
)
def test_create_console_output(query, rowcount, expected):
    """
    Debe generar el mensaje adecuado.
    """

    result = MagicMock()
    result.rowcount = rowcount

    assert manager._create_console_output(query, result) == expected


# =============================================================================
# _extract_table_name
# =============================================================================


def test_extract_table_name():
    """
    Debe extraer correctamente el nombre de tabla.
    """

    assert manager._extract_table_name("SELECT * FROM users") == "users"


def test_extract_table_name_with_semicolon():
    """
    Debe eliminar el punto y coma final.
    """

    assert manager._extract_table_name("SELECT * FROM users;") == "users"


def test_extract_table_name_invalid():
    """
    Debe devolver None cuando no pueda extraerse.
    """

    assert manager._extract_table_name("SELECT") is None


# =============================================================================
# _get_primary_key_columns
# =============================================================================


def test_get_primary_key_columns(monkeypatch):
    """
    Debe recuperar las columnas PK mediante inspect().
    """

    inspector = MagicMock()
    inspector.get_pk_constraint.return_value = {"constrained_columns": ["id"]}

    monkeypatch.setattr(manager, "inspect", MagicMock(return_value=inspector))

    engine = MagicMock()

    result = manager._get_primary_key_columns(engine, "users")

    assert result == ["id"]


def test_get_primary_key_columns_without_pk(monkeypatch):
    """
    Debe devolver lista vacía si no existe PK.
    """

    inspector = MagicMock()
    inspector.get_pk_constraint.return_value = {}

    monkeypatch.setattr(manager, "inspect", MagicMock(return_value=inspector))

    engine = MagicMock()

    result = manager._get_primary_key_columns(engine, "users")

    assert result == []


# =============================================================================
# _get_editable_metadata
# =============================================================================


def test_get_editable_metadata(monkeypatch):
    """
    Debe recuperar la información de edición.
    """

    monkeypatch.setattr(
        manager,
        "_get_primary_key_columns",
        MagicMock(return_value=["id"]),
    )

    engine = MagicMock()

    table, pk = manager._get_editable_metadata(
        "SELECT * FROM users",
        engine,
    )

    assert table == "users"
    assert pk == ["id"]


def test_get_editable_metadata_non_editable():
    """
    Debe devolver valores vacíos para consultas no editables.
    """

    engine = MagicMock()

    table, pk = manager._get_editable_metadata(
        "SELECT id FROM users",
        engine,
    )

    assert table is None
    assert pk == []


def test_get_editable_metadata_without_table(monkeypatch):
    """
    Debe devolver valores vacíos si no puede extraerse la tabla.
    """

    monkeypatch.setattr(
        manager,
        "_extract_table_name",
        MagicMock(return_value=None),
    )

    monkeypatch.setattr(
        manager,
        "is_editable_query",
        MagicMock(return_value=True),
    )

    engine = MagicMock()

    table, pk = manager._get_editable_metadata(
        "SELECT * FROM",
        engine,
    )

    assert table is None
    assert pk == []

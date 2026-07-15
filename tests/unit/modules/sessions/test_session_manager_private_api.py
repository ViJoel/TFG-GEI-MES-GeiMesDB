from unittest.mock import MagicMock

import pytest

import modules.sessions.manager as manager
from entities.query_result import ResultSet

# =============================================================================
# _create_query_result
# =============================================================================


def test_create_query_result(monkeypatch):
    """
    Debe construir correctamente un QueryResult.
    """

    result_set = ResultSet(
        rows=[[1], [2]],
        columns=["id"],
        table_metadata=None,
    )

    monkeypatch.setattr(
        manager,
        "_create_result_set",
        MagicMock(return_value=result_set),
    )

    monkeypatch.setattr(
        manager,
        "_format_result_set",
        MagicMock(return_value="TABLE"),
    )

    result = manager._create_query_result(
        engine=MagicMock(),
        query="SELECT * FROM users",
        result=MagicMock(),
    )

    assert result.success is True
    assert result.result_set is result_set
    assert result.console_output == "TABLE\n\n2 row(s) returned."


# =============================================================================
# _create_result_set
# =============================================================================


def test_create_result_set_not_editable(monkeypatch):
    """
    No debe reflejar metadatos cuando la consulta
    no es editable.
    """

    result = MagicMock()
    result.keys.return_value = ["id", "name"]
    result.fetchall.return_value = [
        (1, "Alice"),
        (2, "Bob"),
    ]

    monkeypatch.setattr(
        manager,
        "is_editable_query",
        MagicMock(return_value=False),
    )

    result_set = manager._create_result_set(
        engine=MagicMock(),
        query="SELECT id FROM users",
        result=result,
    )

    assert result_set.columns == ["id", "name"]
    assert result_set.rows == [
        [1, "Alice"],
        [2, "Bob"],
    ]
    assert result_set.table_metadata is None


def test_create_result_set_editable(monkeypatch):
    """
    Debe reflejar metadatos cuando la consulta
    es editable.
    """

    metadata = MagicMock()

    result = MagicMock()
    result.keys.return_value = ["id"]
    result.fetchall.return_value = [(1,)]

    monkeypatch.setattr(
        manager,
        "is_editable_query",
        MagicMock(return_value=True),
    )

    monkeypatch.setattr(
        manager,
        "_extract_table_name",
        MagicMock(return_value="users"),
    )

    reflect = MagicMock(return_value=metadata)

    monkeypatch.setattr(
        manager,
        "_reflect_table_metadata",
        reflect,
    )

    engine = MagicMock()

    result_set = manager._create_result_set(
        engine=engine,
        query="SELECT * FROM users",
        result=result,
    )

    assert result_set.table_metadata is metadata

    reflect.assert_called_once_with(
        engine=engine,
        table_name="users",
    )


def test_create_result_set_editable_without_table_name(monkeypatch):
    """
    Si no puede obtener el nombre de la tabla no
    debe reflejar metadatos.
    """

    result = MagicMock()
    result.keys.return_value = []
    result.fetchall.return_value = []

    monkeypatch.setattr(
        manager,
        "is_editable_query",
        MagicMock(return_value=True),
    )

    monkeypatch.setattr(
        manager,
        "_extract_table_name",
        MagicMock(return_value=None),
    )

    reflect = MagicMock()

    monkeypatch.setattr(
        manager,
        "_reflect_table_metadata",
        reflect,
    )

    result_set = manager._create_result_set(
        engine=MagicMock(),
        query="SELECT * FROM users",
        result=result,
    )

    assert result_set.table_metadata is None
    reflect.assert_not_called()


# =============================================================================
# _reflect_table_metadata
# =============================================================================


def test_reflect_table_metadata(monkeypatch):
    """
    Debe construir correctamente un TableMetadata
    reflejando la tabla mediante SQLAlchemy.
    """

    table = MagicMock()

    table_ctor = MagicMock(return_value=table)

    monkeypatch.setattr(
        manager,
        "Table",
        table_ctor,
    )

    metadata_ctor = MagicMock(return_value="metadata")

    monkeypatch.setattr(
        manager,
        "TableMetadata",
        metadata_ctor,
    )

    engine = MagicMock()

    returned = manager._reflect_table_metadata(
        engine=engine,
        table_name="users",
    )

    assert returned == "metadata"

    table_ctor.assert_called_once()

    metadata_ctor.assert_called_once_with(
        table=table,
    )


# =============================================================================
# _format_result_set
# =============================================================================


def test_format_result_set():
    """
    Debe generar una representación tabular del
    ResultSet.
    """

    result_set = ResultSet(
        rows=[
            [1, "Alice"],
            [20, "Bob"],
        ],
        columns=[
            "id",
            "name",
        ],
        table_metadata=None,
    )

    assert manager._format_result_set(result_set) == (
        "id | name \n" "---+------\n" "1  | Alice\n" "20 | Bob  "
    )


# =============================================================================
# _create_console_output
# =============================================================================


@pytest.mark.parametrize(
    ("query", "rowcount", "expected"),
    [
        ("INSERT INTO users VALUES (1)", 3, "3 row(s) inserted."),
        ("UPDATE users SET name='A'", 5, "5 row(s) updated."),
        ("DELETE FROM users", 2, "2 row(s) deleted."),
        ("CREATE TABLE users(id INTEGER)", 0, "Query executed successfully."),
    ],
)
def test_create_console_output(
    query,
    rowcount,
    expected,
):
    """
    Debe generar el mensaje adecuado según el
    comando SQL ejecutado.
    """

    result = MagicMock()
    result.rowcount = rowcount

    assert (
        manager._create_console_output(
            query=query,
            result=result,
        )
        == expected
    )


# =============================================================================
# _extract_table_name
# =============================================================================


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ("SELECT * FROM users", "users"),
        ("SELECT * FROM users;", "users"),
        (" SELECT   *   FROM   users ", "users"),
        ("SELECT * FROM schema.users", "schema.users"),
    ],
)
def test_extract_table_name(
    query,
    expected,
):
    """
    Debe extraer correctamente el nombre de la
    tabla objetivo.
    """

    assert manager._extract_table_name(query) == expected


def test_extract_table_name_invalid():
    """
    Si la consulta no contiene suficientes
    elementos debe devolver None.
    """

    assert manager._extract_table_name("SELECT *") is None

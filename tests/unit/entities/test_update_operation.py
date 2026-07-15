from sqlalchemy import (
    Column,
    Integer,
    MetaData,
    String,
    Table,
)

from entities.table_metadata import TableMetadata
from entities.update_operation import UpdateOperation

# =============================================================================
# FIXTURES
# =============================================================================


def create_metadata():
    """
    Crea una tabla sencilla para las pruebas.
    """

    table = Table(
        "users",
        MetaData(),
        Column("id", Integer, primary_key=True),
        Column("name", String),
        Column("age", Integer),
    )

    return TableMetadata(table=table)


# =============================================================================
# TO STATEMENT
# =============================================================================


def test_to_statement_generates_update_statement():
    """
    Debe generar una sentencia UPDATE con la
    cláusula WHERE y los valores modificados.
    """

    metadata = create_metadata()

    operation = UpdateOperation(
        table_metadata=metadata,
        primary_key={"id": 1},
        values={"name": "John"},
    )

    stmt = operation.to_statement()

    sql = str(
        stmt.compile(
            compile_kwargs={
                "literal_binds": True,
            }
        )
    )

    assert "UPDATE users" in sql
    assert "SET name='John'" in sql
    assert "WHERE users.id = 1" in sql


def test_to_statement_supports_composite_primary_key():
    """
    Debe generar una cláusula WHERE con todas las
    columnas de una clave primaria compuesta.
    """

    table = Table(
        "users",
        MetaData(),
        Column("id", Integer, primary_key=True),
        Column("version", Integer, primary_key=True),
        Column("name", String),
    )

    metadata = TableMetadata(table=table)

    operation = UpdateOperation(
        table_metadata=metadata,
        primary_key={
            "id": 1,
            "version": 2,
        },
        values={
            "name": "John",
        },
    )

    sql = str(
        operation.to_statement().compile(
            compile_kwargs={
                "literal_binds": True,
            }
        )
    )

    assert "users.id = 1" in sql
    assert "users.version = 2" in sql


# =============================================================================
# TO SQL
# =============================================================================


def test_to_sql_generates_literal_sql():
    """
    Debe generar la representación SQL de la
    operación.
    """

    from sqlalchemy.dialects.sqlite import dialect

    metadata = create_metadata()

    operation = UpdateOperation(
        table_metadata=metadata,
        primary_key={"id": 1},
        values={"name": "John"},
    )

    sql = operation.to_sql(dialect())

    assert "UPDATE users" in sql
    assert "SET name='John'" in sql
    assert "WHERE users.id = 1" in sql

from datetime import (
    date,
    datetime,
    time,
)
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from sqlalchemy.sql.sqltypes import (
    JSON,
    Boolean,
    Date,
    DateTime,
    Float,
    Integer,
    Numeric,
    String,
    Time,
    Uuid,
)

from entities.table_metadata import TableMetadata

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def metadata():
    """
    Crea un TableMetadata con todos los tipos
    necesarios para las pruebas.
    """

    table = MagicMock()

    table.name = "users"

    id_column = MagicMock()
    id_column.name = "id"
    id_column.type = Integer()

    name_column = MagicMock()
    name_column.name = "name"
    name_column.type = String()

    active_column = MagicMock()
    active_column.name = "active"
    active_column.type = Boolean()

    table.columns = [
        id_column,
        name_column,
        active_column,
    ]

    table.primary_key.columns = [id_column]

    return TableMetadata(table=table)


# =============================================================================
# POST INIT
# =============================================================================


def test_post_init_extracts_table_information(metadata):
    """
    Debe extraer correctamente la información de
    la tabla reflejada.
    """

    assert metadata.table_name == "users"
    assert metadata.primary_key_columns == ["id"]

    assert isinstance(metadata.column_types["id"], Integer)
    assert isinstance(metadata.column_types["name"], String)
    assert isinstance(metadata.column_types["active"], Boolean)


# =============================================================================
# CONVERT VALUE
# =============================================================================


@pytest.mark.parametrize(
    ("column_type", "value", "expected"),
    [
        (Integer(), "12", 12),
        (Float(), "1.5", 1.5),
        (Numeric(), "10.25", Decimal("10.25")),
        (String(), "hello", "hello"),
        (Boolean(), "true", True),
        (Boolean(), "false", False),
        (Date(), "2024-01-01", date(2024, 1, 1)),
        (
            DateTime(),
            "2024-01-01T10:30:00",
            datetime(2024, 1, 1, 10, 30, 0),
        ),
        (Time(), "12:30:45", time(12, 30, 45)),
        (JSON(), '{"a":1}', {"a": 1}),
        (
            Uuid(),
            "550e8400-e29b-41d4-a716-446655440000",
            "550e8400-e29b-41d4-a716-446655440000",
        ),
    ],
)
def test_convert_value(metadata, column_type, value, expected):
    """
    Debe convertir correctamente cada tipo
    soportado.
    """

    metadata.column_types = {"col": column_type}

    assert metadata.convert_value("col", value) == expected


# =============================================================================
# NULL VALUES
# =============================================================================


@pytest.mark.parametrize(
    "value",
    [
        "",
        "NULL",
        "[NULL]",
        " null ",
    ],
)
def test_convert_value_returns_none_for_null_values(metadata, value):
    """
    Debe interpretar las distintas
    representaciones de NULL.
    """

    metadata.column_types = {"col": String()}

    assert metadata.convert_value("col", value) is None


# =============================================================================
# INVALID CONVERSIONS
# =============================================================================


@pytest.mark.parametrize(
    ("column_type", "value"),
    [
        (Integer(), "abc"),
        (Float(), "abc"),
        (Numeric(), "abc"),
        (Date(), "abc"),
        (DateTime(), "abc"),
        (Time(), "abc"),
        (JSON(), "{invalid"),
    ],
)
def test_convert_value_returns_original_value_when_conversion_fails(
    metadata,
    column_type,
    value,
):
    """
    Si la conversión falla debe devolverse el
    valor original.
    """

    metadata.column_types = {"col": column_type}

    assert metadata.convert_value("col", value) == value


# =============================================================================
# UNKNOWN TYPE
# =============================================================================


def test_convert_value_unknown_type_returns_original_value(metadata):
    """
    Tipos no soportados deben devolver el valor
    original.
    """

    class CustomType:
        pass

    metadata.column_types = {"col": CustomType()}

    assert metadata.convert_value("col", "hello") == "hello"

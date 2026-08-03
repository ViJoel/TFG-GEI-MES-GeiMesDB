from unittest.mock import (
    MagicMock,
    patch,
)

import pytest
from sqlalchemy.sql.sqltypes import (
    Boolean,
    Integer,
    String,
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


def test_convert_value_delegates_to_input_converter(metadata):
    """
    Debe delegar la conversión en input_converter.
    """

    metadata.column_types = {"col": Integer()}

    with patch(
        "entities.table_metadata.input_converter",
        return_value=123,
    ) as mock_converter:

        result = metadata.convert_value(
            "col",
            "12",
        )

    mock_converter.assert_called_once_with(
        column_type=metadata.column_types["col"],
        value="12",
    )

    assert result == 123


# =============================================================================
# SUPPORTS EDITTING
# =============================================================================


def test_supports_editing_delegates_to_supports_input_conversion(metadata):
    """
    Debe consultar si el tipo admite edición.
    """

    metadata.column_types = {"col": Integer()}

    with patch(
        "entities.table_metadata.supports_input_conversion",
        return_value=True,
    ) as mock_supports:

        result = metadata.supports_editing("col")

    mock_supports.assert_called_once_with(
        metadata.column_types["col"],
    )

    assert result is True


def test_supports_editing_returns_false(metadata):
    """
    Debe devolver False cuando el tipo no admite edición.
    """

    metadata.column_types = {"col": Integer()}

    with patch(
        "entities.table_metadata.supports_input_conversion",
        return_value=False,
    ):

        assert metadata.supports_editing("col") is False

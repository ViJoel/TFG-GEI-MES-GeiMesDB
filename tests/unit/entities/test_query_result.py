from unittest.mock import MagicMock

from entities.query_result import (
    QueryResult,
    ResultSet,
)
from entities.table_metadata import TableMetadata

# =============================================================================
# ResultSet
# =============================================================================


def test_result_set_is_editable_when_table_metadata_exists():
    """
    Un ResultSet debe ser editable cuando existe
    información de la tabla asociada.
    """

    result_set = ResultSet(
        rows=[],
        columns=[],
        table_metadata=MagicMock(spec=TableMetadata),
    )

    assert result_set.is_editable is True


def test_result_set_is_not_editable_when_table_metadata_is_none():
    """
    Un ResultSet no debe ser editable cuando no
    existe información de la tabla asociada.
    """

    result_set = ResultSet(
        rows=[],
        columns=[],
        table_metadata=None,
    )

    assert result_set.is_editable is False


def test_result_set_supports_editing_returns_false_without_metadata():
    """
    Un ResultSet sin metadata nunca debe permitir
    edición de columnas.
    """

    result_set = ResultSet(
        rows=[],
        columns=[],
        table_metadata=None,
    )

    assert result_set.supports_editing("id") is False


def test_result_set_supports_editing_delegates_to_metadata():
    """
    ResultSet debe delegar la comprobación de
    edición en TableMetadata.
    """

    metadata = MagicMock(
        spec=TableMetadata,
    )

    metadata.supports_editing.return_value = True

    result_set = ResultSet(
        rows=[],
        columns=[],
        table_metadata=metadata,
    )

    assert result_set.supports_editing("id") is True

    metadata.supports_editing.assert_called_once_with(
        column_name="id",
    )


def test_result_set_supports_editing_returns_false_for_non_editable_column():
    """
    Una columna no editable debe devolver False.
    """

    metadata = MagicMock(
        spec=TableMetadata,
    )

    metadata.supports_editing.return_value = False

    result_set = ResultSet(
        rows=[],
        columns=[],
        table_metadata=metadata,
    )

    assert result_set.supports_editing("id") is False


# =============================================================================
# QueryResult
# =============================================================================


def test_query_result_stores_values():
    """
    QueryResult debe almacenar correctamente los
    valores recibidos durante su construcción.
    """

    result = QueryResult(
        success=True,
        console_output="Consulta ejecutada correctamente",
        result_set=None,
    )

    assert result.success is True
    assert result.console_output == "Consulta ejecutada correctamente"
    assert result.result_set is None


def test_query_result_stores_result_set():
    """
    QueryResult debe conservar la referencia al
    ResultSet proporcionado.
    """

    result_set = ResultSet(
        rows=[[1, "John"]],
        columns=["id", "name"],
        table_metadata=MagicMock(spec=TableMetadata),
    )

    result = QueryResult(
        success=True,
        console_output="",
        result_set=result_set,
    )

    assert result.result_set is result_set

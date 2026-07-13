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

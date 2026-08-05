from unittest.mock import MagicMock

import pytest

from entities.query_execution import QueryExecution
from entities.query_result import QueryResult

# =============================================================================
# TESTS
# =============================================================================


def test_query_execution_stores_attributes():
    """
    Verifica que la entidad almacena la consulta
    y el resultado proporcionados.
    """

    result = MagicMock(spec=QueryResult)

    execution = QueryExecution(
        query="SELECT * FROM users",
        result=result,
    )

    assert execution.query == "SELECT * FROM users"
    assert execution.result is result


def test_query_execution_uses_slots():
    """
    Verifica que la entidad no permite crear
    atributos dinámicos.
    """

    execution = QueryExecution(
        query="SELECT 1",
        result=MagicMock(spec=QueryResult),
    )

    with pytest.raises(AttributeError):
        execution.new_attribute = "value"

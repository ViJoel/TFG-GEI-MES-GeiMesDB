from unittest.mock import MagicMock

import modules.sessions.manager as manager
from entities.query_result import QueryResult

# =============================================================================
# execute_script
# =============================================================================


def test_execute_script_all_success(monkeypatch):
    """
    Debe marcar todas las consultas como correctas cuando
    execute_query devuelve éxito.
    """

    monkeypatch.setattr(
        manager,
        "execute_query",
        MagicMock(
            return_value=QueryResult(
                success=True,
                console_output="OK",
                result_set=None,
            )
        ),
    )

    queries = [
        "SELECT 1",
        "SELECT 2",
        "SELECT 3",
    ]

    result = manager.execute_script("1", queries)

    assert len(result.items) == 3

    for item, query in zip(result.items, queries):
        assert item.query == query
        assert item.error is None

    assert manager.execute_query.call_count == 3


def test_execute_script_all_errors(monkeypatch):
    """
    Debe registrar el error de cada consulta cuando todas fallan.
    """

    monkeypatch.setattr(
        manager,
        "execute_query",
        MagicMock(
            return_value=QueryResult(
                success=False,
                console_output="SQL Error",
                result_set=None,
            )
        ),
    )

    queries = [
        "SELECT 1",
        "SELECT 2",
    ]

    result = manager.execute_script("1", queries)

    assert len(result.items) == 2

    for item in result.items:
        assert item.error == "SQL Error"

    assert manager.execute_query.call_count == 2


def test_execute_script_mixed_results(monkeypatch):
    """
    Debe combinar correctamente consultas correctas y erróneas.
    """

    manager.execute_query = MagicMock(
        side_effect=[
            QueryResult(
                success=True,
                console_output="OK",
                result_set=None,
            ),
            QueryResult(
                success=False,
                console_output="Syntax error",
                result_set=None,
            ),
            QueryResult(
                success=True,
                console_output="OK",
                result_set=None,
            ),
        ]
    )

    queries = [
        "SELECT 1",
        "BAD SQL",
        "SELECT 2",
    ]

    result = manager.execute_script("1", queries)

    assert len(result.items) == 3

    assert result.items[0].error is None
    assert result.items[1].error == "Syntax error"
    assert result.items[2].error is None

    assert manager.execute_query.call_count == 3


def test_execute_script_empty():
    """
    Debe devolver un resultado vacío cuando no hay consultas.
    """

    result = manager.execute_script("1", [])

    assert result.items == []

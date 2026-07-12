from entities.query_result import (
    QueryResult,
    ResultSet,
)

# =============================================================================
# ResultSet
# =============================================================================


def test_result_set_is_editable_when_table_has_primary_key():
    """
    Un ResultSet debe ser editable cuando existe
    una tabla asociada y al menos una columna de
    clave primaria.
    """

    result_set = ResultSet(
        rows=[],
        columns=[],
        columns_types=[],
        table_name="actor",
        primary_key_columns=["actor_id"],
    )

    assert result_set.is_editable is True


def test_result_set_is_not_editable_when_table_name_is_none():
    """
    Un ResultSet no debe ser editable si no está
    asociado a ninguna tabla.
    """

    result_set = ResultSet(
        rows=[],
        columns=[],
        columns_types=[],
        table_name=None,
        primary_key_columns=["actor_id"],
    )

    assert result_set.is_editable is False


def test_result_set_is_not_editable_when_primary_key_is_empty():
    """
    Un ResultSet no debe ser editable si la tabla
    no dispone de clave primaria.
    """

    result_set = ResultSet(
        rows=[],
        columns=[],
        columns_types=[],
        table_name="actor",
        primary_key_columns=[],
    )

    assert result_set.is_editable is False


def test_result_set_is_not_editable_when_table_name_is_none_and_primary_key_is_empty():
    """
    Un ResultSet no debe ser editable cuando no
    existe tabla asociada ni clave primaria.
    """

    result_set = ResultSet(
        rows=[],
        columns=[],
        columns_types=[],
        table_name=None,
        primary_key_columns=[],
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
        columns_types=[int, str],
        table_name="actor",
        primary_key_columns=["id"],
    )

    result = QueryResult(
        success=True,
        console_output="",
        result_set=result_set,
    )

    assert result.result_set is result_set

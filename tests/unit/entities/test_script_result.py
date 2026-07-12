from entities.script_result import (
    ScriptResult,
    ScriptResultItem,
)

# =============================================================================
# ScriptResultItem
# =============================================================================


def test_script_result_item_is_successful_when_error_is_none():
    """
    Un ScriptResultItem debe indicar éxito cuando
    no existe ningún mensaje de error.
    """
    item = ScriptResultItem(
        query="SELECT * FROM actor;",
        error=None,
    )

    assert item.success is True


def test_script_result_item_is_not_successful_when_error_exists():
    """
    Un ScriptResultItem no debe indicar éxito
    cuando existe un mensaje de error.
    """
    item = ScriptResultItem(
        query="SELECT * FROM actor;",
        error="La tabla no existe.",
    )

    assert item.success is False


# =============================================================================
# ScriptResult
# =============================================================================


def test_script_result_stores_items():
    """
    ScriptResult debe conservar la lista de
    resultados individuales proporcionada.
    """
    items = [
        ScriptResultItem(query="SELECT 1;"),
        ScriptResultItem(
            query="SELECT * FROM tabla;",
            error="La tabla no existe.",
        ),
    ]

    result = ScriptResult(items=items)

    assert result.items is items


def test_script_result_can_store_empty_items_list():
    """
    ScriptResult debe permitir almacenar una
    lista vacía de resultados.
    """
    result = ScriptResult(items=[])

    assert result.items == []

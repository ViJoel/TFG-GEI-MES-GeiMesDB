from decimal import Decimal

from modules.conversions.display_decimal import DisplayDecimal
from modules.conversions.display_normalizers import (
    normalize,
    normalize_decimal,
)

# =============================================================================
# DECIMAL
# =============================================================================


def test_normalize_decimal_returns_display_decimal():
    """
    Un Decimal debe convertirse a DisplayDecimal.
    """

    result = normalize_decimal(
        Decimal("10.50"),
    )

    assert isinstance(
        result,
        DisplayDecimal,
    )

    assert result.value == "10.50"


def test_normalize_decimal_preserves_decimal_representation():
    """
    La representación textual del Decimal debe
    mantenerse.
    """

    result = normalize(
        Decimal("0.0001"),
    )

    assert str(result) == "0.0001"


# =============================================================================
# SIMPLE VALUES
# =============================================================================


def test_normalize_returns_original_value_for_unknown_types():
    """
    Los tipos no soportados deben devolverse
    sin cambios.
    """

    value = object()

    assert normalize(value) is value


def test_normalize_returns_strings_without_changes():
    """
    Las cadenas no necesitan normalización.
    """

    value = "hello"

    assert normalize(value) == value


# =============================================================================
# LISTS
# =============================================================================


def test_normalize_list_is_recursive():
    """
    Las listas deben normalizar sus elementos
    internos.
    """

    value = [
        Decimal("10.5"),
        "hello",
    ]

    result = normalize(value)

    assert isinstance(
        result[0],
        DisplayDecimal,
    )

    assert result[1] == "hello"


# =============================================================================
# TUPLES
# =============================================================================


def test_normalize_tuple_is_recursive():
    """
    Las tuplas deben conservar su tipo y
    normalizar sus elementos.
    """

    value = (
        Decimal("1.5"),
        "test",
    )

    result = normalize(value)

    assert isinstance(
        result,
        tuple,
    )

    assert isinstance(
        result[0],
        DisplayDecimal,
    )


# =============================================================================
# SETS
# =============================================================================


def test_normalize_set_is_recursive():
    """
    Los sets deben normalizar sus elementos.
    """

    value = {
        Decimal("1.5"),
    }

    result = normalize(value)

    assert isinstance(
        result,
        set,
    )

    assert DisplayDecimal("1.5") in result


# =============================================================================
# DICTS
# =============================================================================


def test_normalize_dict_is_recursive():
    """
    Los diccionarios deben normalizar sus valores.
    """

    value = {
        "price": Decimal("20.5"),
    }

    result = normalize(value)

    assert isinstance(
        result["price"],
        DisplayDecimal,
    )


# =============================================================================
# NESTED STRUCTURES
# =============================================================================


def test_normalize_nested_structure():
    """
    La normalización debe aplicarse de forma
    recursiva en estructuras complejas.
    """

    value = {
        "items": [
            {
                "price": Decimal("5.25"),
            },
        ],
    }

    result = normalize(value)

    normalized_decimal = result["items"][0]["price"]

    assert isinstance(
        normalized_decimal,
        DisplayDecimal,
    )

    assert str(normalized_decimal) == "5.25"

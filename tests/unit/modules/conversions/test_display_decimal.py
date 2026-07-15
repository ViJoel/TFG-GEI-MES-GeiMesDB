from modules.conversions.display_decimal import DisplayDecimal

# =============================================================================
# INITIALIZATION
# =============================================================================


def test_display_decimal_stores_value():
    """
    Debe conservar el valor recibido.
    """

    decimal = DisplayDecimal("10.50")

    assert decimal.value == "10.50"


# =============================================================================
# STRING REPRESENTATION
# =============================================================================


def test_display_decimal_str_returns_value():
    """
    str() debe devolver directamente el valor
    almacenado.
    """

    decimal = DisplayDecimal("10.50")

    assert str(decimal) == "10.50"


def test_display_decimal_repr_returns_value():
    """
    repr() debe devolver el valor almacenado para
    que las colecciones se visualicen correctamente.
    """

    decimal = DisplayDecimal("10.50")

    assert repr(decimal) == "10.50"


# =============================================================================
# IMMUTABILITY
# =============================================================================


def test_display_decimal_is_immutable():
    """
    Al ser frozen no debe permitir modificaciones.
    """

    decimal = DisplayDecimal("10.50")

    try:
        decimal.value = "20.00"

    except Exception:
        pass

    else:
        raise AssertionError(
            "DisplayDecimal should be immutable",
        )

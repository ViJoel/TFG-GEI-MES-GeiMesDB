from datetime import (
    date,
    datetime,
    time,
)
from decimal import Decimal
from uuid import UUID

import pytest

from modules.conversions.python_converters import (
    convert_boolean,
    convert_date,
    convert_datetime,
    convert_float,
    convert_integer,
    convert_numeric,
    convert_string,
    convert_time,
    convert_uuid,
)

# =============================================================================
# BOOLEAN
# =============================================================================


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        # True
        ("true", True),
        ("TRUE", True),
        (" True ", True),
        ("t", True),
        ("T", True),
        ("1", True),
        ("yes", True),
        ("YES", True),
        (" y ", True),
        ("si", True),
        ("SI", True),
        ("s", True),
        ("on", True),
        # False
        ("false", False),
        ("FALSE", False),
        (" False ", False),
        ("f", False),
        ("F", False),
        ("0", False),
        ("no", False),
        ("NO", False),
        (" n ", False),
        ("off", False),
    ],
)
def test_convert_boolean(value, expected):
    """
    Los valores booleanos válidos deben convertirse
    correctamente ignorando mayúsculas, minúsculas
    y espacios.
    """

    assert convert_boolean(value) is expected


@pytest.mark.parametrize(
    "value",
    [
        "anything",
        "invalid",
        "maybe",
        "",
        "null",
        "2",
    ],
)
def test_convert_boolean_invalid_values_raise_error(value):
    """
    Los valores no reconocidos deben provocar un
    error de conversión.
    """

    with pytest.raises(ValueError):
        convert_boolean(value)


# =============================================================================
# DATE / DATETIME / TIME
# =============================================================================


def test_convert_date():
    """
    Una fecha ISO debe convertirse a date.
    """

    result = convert_date(
        "2024-01-01",
    )

    assert result == date(
        2024,
        1,
        1,
    )


def test_convert_datetime():
    """
    Un datetime ISO debe convertirse correctamente.
    """

    result = convert_datetime(
        "2024-01-01T12:30:00",
    )

    assert result == datetime(
        2024,
        1,
        1,
        12,
        30,
    )


def test_convert_time():
    """
    Una hora ISO debe convertirse correctamente.
    """

    result = convert_time(
        "12:30:45",
    )

    assert result == time(
        12,
        30,
        45,
    )


# =============================================================================
# NUMBERS
# =============================================================================


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("10", 10),
        ("-5", -5),
        ("0", 0),
    ],
)
def test_convert_integer(value, expected):
    """
    Los enteros deben convertirse correctamente.
    """

    assert convert_integer(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("10.5", 10.5),
        ("10,5", 10.5),
        (" 10.5 ", 10.5),
        ("1 000,5", 1000.5),
    ],
)
def test_convert_float(value, expected):
    """
    Los float deben aceptar espacios y coma decimal.
    """

    assert convert_float(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("10.50", Decimal("10.50")),
        ("10,50", Decimal("10.50")),
        (" 10,50 ", Decimal("10.50")),
        ("1 000,50", Decimal("1000.50")),
    ],
)
def test_convert_numeric(value, expected):
    """
    Los Decimal deben aceptar distintos formatos
    de entrada.
    """

    assert convert_numeric(value) == expected


# =============================================================================
# STRING
# =============================================================================


def test_convert_string_returns_original_value():
    """
    Las cadenas deben mantenerse sin cambios.
    """

    value = "hello world"

    assert convert_string(value) == value


# =============================================================================
# UUID
# =============================================================================


def test_convert_uuid():
    """
    Un UUID textual debe convertirse a UUID.
    """

    value = "550e8400-e29b-41d4-a716-446655440000"

    result = convert_uuid(value)

    assert isinstance(
        result,
        UUID,
    )

    assert str(result) == value

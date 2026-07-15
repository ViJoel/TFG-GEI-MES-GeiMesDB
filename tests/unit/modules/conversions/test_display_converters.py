from datetime import (
    date,
    datetime,
    time,
)
from decimal import Decimal

import pytest

from modules.conversions.display_converters import (
    convert_boolean,
    convert_date,
    convert_datetime,
    convert_decimal,
    convert_default,
    convert_dict,
    convert_float,
    convert_integer,
    convert_list,
    convert_none,
    convert_set,
    convert_string,
    convert_time,
    convert_tuple,
)

# =============================================================================
# SIMPLE TYPES
# =============================================================================


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (True, "TRUE"),
        (False, "FALSE"),
    ],
)
def test_convert_boolean(value, expected):
    """
    Los booleanos deben convertirse usando
    su representación textual Python.
    """

    assert convert_boolean(value) == expected


def test_convert_date():
    """
    Las fechas deben convertirse a formato ISO.
    """

    value = date(2024, 1, 1)

    assert convert_date(value) == "2024-01-01"


def test_convert_datetime():
    """
    Los datetime deben convertirse a formato ISO.
    """

    value = datetime(2024, 1, 1, 12, 30)

    assert convert_datetime(value) == "2024-01-01T12:30:00"


def test_convert_time():
    """
    Las horas deben convertirse a formato ISO.
    """

    value = time(12, 30, 45)

    assert convert_time(value) == "12:30:45"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (Decimal("10.5"), "10.5"),
        (Decimal("0"), "0"),
    ],
)
def test_convert_decimal(value, expected):
    """
    Los Decimal deben convertirse mediante str.
    """

    assert convert_decimal(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (1.5, "1.5"),
        (0.0, "0.0"),
    ],
)
def test_convert_float(value, expected):
    """
    Los float deben convertirse mediante str.
    """

    assert convert_float(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (1, "1"),
        (0, "0"),
    ],
)
def test_convert_integer(value, expected):
    """
    Los enteros deben convertirse mediante str.
    """

    assert convert_integer(value) == expected


def test_convert_string_returns_same_value():
    """
    Las cadenas deben mantenerse sin cambios.
    """

    value = "hello"

    assert convert_string(value) == value


def test_convert_none():
    """
    None debe representarse como NULL visual.
    """

    assert convert_none(None) == "[NULL]"


def test_convert_default():
    """
    Tipos no soportados deben usar str().
    """

    value = object()

    assert convert_default(value) == str(value)


# =============================================================================
# COLLECTIONS
# =============================================================================


def test_convert_dict():
    """
    Los diccionarios deben convertirse a JSON.
    """

    value = {
        "name": "John",
        "age": 30,
    }

    assert convert_dict(value) == '{"name": "John", "age": 30}'


def test_convert_list():
    """
    Las listas deben convertirse a texto.
    """

    value = [
        1,
        2,
        3,
    ]

    assert convert_list(value) == "[1, 2, 3]"


def test_convert_tuple():
    """
    Las tuplas deben convertirse a texto.
    """

    value = (
        1,
        2,
    )

    assert convert_tuple(value) == "(1, 2)"


def test_convert_set():
    """
    Los sets deben convertirse a texto.
    """

    value = {
        1,
        2,
    }

    result = convert_set(value)

    assert result in (
        "{1, 2}",
        "{2, 1}",
    )

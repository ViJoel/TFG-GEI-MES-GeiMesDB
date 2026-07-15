from datetime import (
    date,
    datetime,
    time,
)
from decimal import Decimal
from uuid import UUID

import pytest
from sqlalchemy.sql.sqltypes import (
    Boolean,
    Date,
    DateTime,
    Float,
    Integer,
    Numeric,
    String,
    Time,
    Uuid,
)

from modules.conversions.converters import (
    display_converter,
    input_converter,
    supports_input_conversion,
)

# =============================================================================
# INPUT CONVERTER
# =============================================================================


@pytest.mark.parametrize(
    ("column_type", "value", "expected"),
    [
        (Boolean(), "true", True),
        (Boolean(), "false", False),
        (Integer(), "123", 123),
        (Float(), "1.5", 1.5),
        (Numeric(), "10.25", Decimal("10.25")),
        (String(), "hello", "hello"),
        (Date(), "2024-01-01", date(2024, 1, 1)),
        (
            DateTime(),
            "2024-01-01T10:30:00",
            datetime(2024, 1, 1, 10, 30),
        ),
        (
            Time(),
            "12:30:45",
            time(12, 30, 45),
        ),
        (
            Uuid(),
            "550e8400-e29b-41d4-a716-446655440000",
            UUID("550e8400-e29b-41d4-a716-446655440000"),
        ),
    ],
)
def test_input_converter_supported_types(
    column_type,
    value,
    expected,
):
    """
    Los tipos SQLAlchemy soportados deben
    convertirse correctamente.
    """

    assert (
        input_converter(
            column_type,
            value,
        )
        == expected
    )


@pytest.mark.parametrize(
    "value",
    [
        "",
        "NULL",
        "[NULL]",
        " null ",
    ],
)
def test_input_converter_null_values_return_none(value):
    """
    Las representaciones de NULL deben convertirse
    a None.
    """

    assert (
        input_converter(
            String(),
            value,
        )
        is None
    )


@pytest.mark.parametrize(
    ("column_type", "value"),
    [
        (Integer(), "abc"),
        (Float(), "abc"),
        (Numeric(), "abc"),
        (Date(), "invalid"),
        (DateTime(), "invalid"),
        (Time(), "invalid"),
        (Boolean(), "invalid"),
    ],
)
def test_input_converter_invalid_values_return_original(
    column_type,
    value,
):
    """
    Si la conversión falla se conserva el valor
    original.
    """

    assert (
        input_converter(
            column_type,
            value,
        )
        == value
    )


def test_input_converter_unknown_type_returns_original():
    """
    Los tipos SQLAlchemy no soportados deben
    devolver el valor original.
    """

    class CustomType:
        pass

    assert (
        input_converter(
            CustomType(),
            "hello",
        )
        == "hello"
    )


# =============================================================================
# DISPLAY CONVERTER
# =============================================================================


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, "[NULL]"),
        (True, "TRUE"),
        (False, "FALSE"),
        (Decimal("10.5"), "10.5"),
        (1, "1"),
        (1.5, "1.5"),
        ("hello", "hello"),
        (
            date(2024, 1, 1),
            "2024-01-01",
        ),
        (
            datetime(2024, 1, 1, 10, 30),
            "2024-01-01T10:30:00",
        ),
        (
            time(12, 30),
            "12:30:00",
        ),
        (
            {"a": 1},
            '{"a": 1}',
        ),
        (
            [1, 2],
            "[1, 2]",
        ),
        (
            (1, 2),
            "(1, 2)",
        ),
        (
            {1, 2},
            "{1, 2}",
        ),
    ],
)
def test_display_converter_supported_types(
    value,
    expected,
):
    """
    Los tipos Python soportados deben convertirse
    a texto correctamente.
    """

    assert display_converter(value) == expected


def test_display_converter_unknown_type_uses_default():
    """
    Los tipos no registrados deben usar el
    conversor por defecto.
    """

    class CustomType:
        pass

    value = CustomType()

    assert display_converter(value) == str(value)


# =============================================================================
# SUPPORTS INPUT CONVERSION
# =============================================================================


@pytest.mark.parametrize(
    "column_type",
    [
        Boolean(),
        Date(),
        DateTime(),
        Float(),
        Integer(),
        Numeric(),
        String(),
        Time(),
        Uuid(),
    ],
)
def test_supports_input_conversion_supported_types(
    column_type,
):
    """
    Los tipos registrados deben admitir edición.
    """

    assert supports_input_conversion(column_type) is True


def test_supports_input_conversion_unknown_type_returns_false():
    """
    Los tipos no registrados no deben admitir
    edición.
    """

    class CustomType:
        pass

    assert supports_input_conversion(CustomType()) is False

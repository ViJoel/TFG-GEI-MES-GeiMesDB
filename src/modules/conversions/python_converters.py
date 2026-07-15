import json
from datetime import (
    date,
    datetime,
    time,
)
from decimal import Decimal
from typing import Any


def convert_integer(
    value: str,
) -> int:
    """
    Convierte un valor textual a un entero.

    Args:
        value (str):
            Valor introducido por el usuario.

    Returns:
        int:
            Valor convertido a entero.
    """

    return int(value)


def convert_float(
    value: str,
) -> float:
    """
    Convierte un valor textual a un número de
    punto flotante.

    Args:
        value (str):
            Valor introducido por el usuario.

    Returns:
        float:
            Valor convertido a punto flotante.
    """

    value = "".join(value.split())
    value = value.replace(",", ".")

    return float(value)


def convert_numeric(
    value: str,
) -> Decimal:
    """
    Convierte un valor textual a un número
    decimal.

    Args:
        value (str):
            Valor introducido por el usuario.

    Returns:
        Decimal:
            Valor convertido a decimal.
    """

    value = "".join(value.split())
    value = value.replace(",", ".")

    return Decimal(value)


def convert_string(
    value: str,
) -> str:
    """
    Devuelve el valor textual sin modificar.

    Args:
        value (str):
            Valor introducido por el usuario.

    Returns:
        str:
            Valor original.
    """

    return value


def convert_boolean(
    value: str,
) -> bool:
    """
    Convierte un valor textual a un booleano.

    Se consideran verdaderos los valores
    'true', '1' y 'yes', ignorando mayúsculas
    y minúsculas.

    Args:
        value (str):
            Valor introducido por el usuario.

    Returns:
        bool:
            Valor convertido a booleano.
    """

    return value.lower() in (
        "true",
        "1",
        "yes",
    )


def convert_date(
    value: str,
) -> date:
    """
    Convierte un valor textual a una fecha.

    Args:
        value (str):
            Fecha en formato ISO.

    Returns:
        date:
            Fecha convertida.
    """

    return date.fromisoformat(value)


def convert_datetime(
    value: str,
) -> datetime:
    """
    Convierte un valor textual a una fecha y
    hora.

    Args:
        value (str):
            Fecha y hora en formato ISO.

    Returns:
        datetime:
            Fecha y hora convertidas.
    """

    return datetime.fromisoformat(value)


def convert_time(
    value: str,
) -> time:
    """
    Convierte un valor textual a una hora.

    Args:
        value (str):
            Hora en formato ISO.

    Returns:
        time:
            Hora convertida.
    """

    return time.fromisoformat(value)


def convert_uuid(
    value: str,
) -> str:
    """
    Devuelve el UUID textual sin modificar.

    Args:
        value (str):
            UUID introducido por el usuario.

    Returns:
        str:
            UUID como cadena.
    """

    return value

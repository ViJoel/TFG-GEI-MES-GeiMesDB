import json
from datetime import (
    date,
    datetime,
    time,
)
from decimal import Decimal
from typing import Any

from modules.conversions.display_normalizers import normalize


def convert_boolean(
    value: bool,
) -> str:
    """
    Convierte un valor booleano a su
    representación textual.

    Args:
        value (bool):
            Valor booleano.

    Returns:
        str:
            Representación textual del valor.
    """

    return str(value)


def convert_date(
    value: date,
) -> str:
    """
    Convierte una fecha a formato ISO.

    Args:
        value (date):
            Fecha.

    Returns:
        str:
            Fecha en formato ISO.
    """

    return value.isoformat()


def convert_datetime(
    value: datetime,
) -> str:
    """
    Convierte una fecha y hora a formato ISO.

    Args:
        value (datetime):
            Fecha y hora.

    Returns:
        str:
            Fecha y hora en formato ISO.
    """

    return value.isoformat()


def convert_decimal(
    value: Decimal,
) -> str:
    """
    Convierte un número decimal a su
    representación textual.

    Args:
        value (Decimal):
            Valor decimal.

    Returns:
        str:
            Representación textual del valor.
    """

    return str(value)


def convert_default(
    value: Any,
) -> str:
    """
    Convierte un valor cualquiera a su
    representación textual por defecto.

    Args:
        value (Any):
            Valor a convertir.

    Returns:
        str:
            Representación textual del valor.
    """

    return str(value)


def convert_dict(
    value: dict[str, Any],
) -> str:
    """
    Convierte un diccionario a formato JSON.

    Args:
        value (dict[str, Any]):
            Diccionario.

    Returns:
        str:
            Representación JSON del diccionario.
    """

    return json.dumps(
        normalize(value),
        ensure_ascii=False,
    )


def convert_float(
    value: float,
) -> str:
    """
    Convierte un número de punto flotante a su
    representación textual.

    Args:
        value (float):
            Valor de punto flotante.

    Returns:
        str:
            Representación textual del valor.
    """

    return str(value)


def convert_integer(
    value: int,
) -> str:
    """
    Convierte un entero a su representación
    textual.

    Args:
        value (int):
            Valor entero.

    Returns:
        str:
            Representación textual del valor.
    """

    return str(value)


def convert_list(
    value: list[Any],
) -> str:
    """
    Convierte una lista a su representación
    textual.

    Args:
        value (list[Any]):
            Lista.

    Returns:
        str:
            Representación textual de la lista.
    """

    return str(normalize(value))


def convert_none(
    value: None,
) -> str:
    """
    Convierte un valor nulo a su representación
    textual para la interfaz.

    Args:
        value (None):
            Valor nulo.

    Returns:
        str:
            Representación textual del valor nulo.
    """

    return "[NULL]"


def convert_set(
    value: set[Any],
) -> str:
    """
    Convierte un conjunto a su representación
    textual.

    Args:
        value (set[Any]):
            Conjunto.

    Returns:
        str:
            Representación textual del conjunto.
    """

    return str(normalize(value))


def convert_string(
    value: str,
) -> str:
    """
    Devuelve una cadena sin modificar.

    Args:
        value (str):
            Cadena de texto.

    Returns:
        str:
            Cadena original.
    """

    return value


def convert_time(
    value: time,
) -> str:
    """
    Convierte una hora a formato ISO.

    Args:
        value (time):
            Hora.

    Returns:
        str:
            Hora en formato ISO.
    """

    return value.isoformat()


def convert_tuple(
    value: tuple[Any, ...],
) -> str:
    """
    Convierte una tupla a su representación
    textual.

    Args:
        value (tuple[Any, ...]):
            Tupla.

    Returns:
        str:
            Representación textual de la tupla.
    """

    return str(normalize(value))

from datetime import (
    date,
    datetime,
    time,
)
from decimal import Decimal
from uuid import UUID


def convert_boolean(
    value: str,
) -> bool:
    """
    Convierte un valor textual a un booleano.

    Valores aceptados:

    - Verdadero:
        - `true`
        - `t`
        - `1`
        - `yes`
        - `y`
        - `si`
        - `s`
        - `on`

    - Falso:
        - `false`
        - `f`
        - `0`
        - `no`
        - `n`
        - `off`

    La comparación ignora mayúsculas,
    minúsculas y espacios.

    Args:
        value (str):
            Valor introducido por el usuario.

    Returns:
        bool:
            Valor convertido a booleano.

    Raises:
        ValueError:
            Si el valor recibido no corresponde
            a una representación booleana válida.
    """

    normalized = "".join(value.split()).lower()

    if normalized in (
        "true",
        "t",
        "1",
        "yes",
        "y",
        "si",
        "s",
        "on",
    ):
        return True

    if normalized in (
        "false",
        "f",
        "0",
        "no",
        "n",
        "off",
    ):
        return False

    raise ValueError(f"Invalid boolean value: {value}")


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
) -> UUID:
    """
    Convierte un valor textual a un objeto UUID.

    Args:
        value (str):
            UUID introducido por el usuario.

    Returns:
        UUID:
            Objeto UUID correspondiente al valor
            introducido.
    """

    return UUID(value)

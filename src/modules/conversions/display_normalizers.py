from decimal import Decimal
from typing import Any

from modules.conversions.display_decimal import DisplayDecimal


def normalize_decimal(
    value: Decimal,
) -> DisplayDecimal:
    """
    Normaliza un valor Decimal para su
    representación visual.

    Args:
        value (Decimal):
            Valor decimal.

    Returns:
        DisplayDecimal:
            Decimal normalizado.
    """

    return DisplayDecimal(str(value))


DISPLAY_NORMALIZERS = {
    Decimal: normalize_decimal,
}


def normalize(
    value: Any,
) -> Any:
    """
    Normaliza un valor Python para facilitar su
    representación visual.

    La normalización se aplica de forma recursiva
    sobre las estructuras de datos compuestas.

    Args:
        value (Any):
            Valor a normalizar.

    Returns:
        Any:
            Valor normalizado.
    """

    if isinstance(value, list):
        return [normalize(item) for item in value]

    if isinstance(value, tuple):
        return tuple(normalize(item) for item in value)

    if isinstance(value, set):
        return {normalize(item) for item in value}

    if isinstance(value, dict):
        return {key: normalize(item) for key, item in value.items()}

    for python_type, normalizer in DISPLAY_NORMALIZERS.items():

        if isinstance(
            value,
            python_type,
        ):
            return normalizer(value)

    return value

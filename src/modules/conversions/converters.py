import json
from datetime import (
    date,
    datetime,
    time,
)
from decimal import (
    Decimal,
    InvalidOperation,
)
from typing import (
    Any,
    Callable,
)

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
from sqlalchemy.types import TypeEngine

import modules.conversions.display_converters as dc
import modules.conversions.python_converters as pc

# =============================================================================
# INPUTS
# =============================================================================


SUPPORTED_INPUT_TYPES: dict[type[TypeEngine], Callable[[str], Any]] = {
    Boolean: pc.convert_boolean,
    Date: pc.convert_date,
    DateTime: pc.convert_datetime,
    Float: pc.convert_float,
    Integer: pc.convert_integer,
    Numeric: pc.convert_numeric,
    String: pc.convert_string,
    Time: pc.convert_time,
    Uuid: pc.convert_uuid,
}


def input_converter(
    column_type: TypeEngine,
    value: str,
) -> Any:
    """
    Convierte un valor textual al tipo Python
    correspondiente según el tipo SQLAlchemy de la
    columna.

    También interpreta distintas representaciones
    de valores nulos (`NULL`, `[NULL]` o cadena
    vacía) como `None`.

    Args:
        column_type (TypeEngine):
            Tipo SQLAlchemy de la columna.

        value (str):
            Valor introducido por el usuario.

    Returns:
        Any:
            Valor convertido al tipo Python
            correspondiente. Si el tipo no está
            soportado o la conversión falla, se
            devuelve el valor original.
    """

    normalized = value.strip().upper().strip("[]")

    if normalized in (
        "",
        "NULL",
    ):
        return None

    try:

        for sqlalchemy_type, converter in SUPPORTED_INPUT_TYPES.items():

            if isinstance(
                column_type,
                sqlalchemy_type,
            ):
                return converter(value)

    except (
        ValueError,
        TypeError,
        InvalidOperation,
        json.JSONDecodeError,
    ):
        pass

    return value


# =============================================================================
# DISPLAY
# =============================================================================

DISPLAY_CONVERTERS: dict[type, Callable[[Any], str]] = {
    type(None): dc.convert_none,
    bool: dc.convert_boolean,
    date: dc.convert_date,
    datetime: dc.convert_datetime,
    Decimal: dc.convert_decimal,
    dict: dc.convert_dict,
    float: dc.convert_float,
    int: dc.convert_integer,
    list: dc.convert_list,
    set: dc.convert_set,
    str: dc.convert_string,
    time: dc.convert_time,
    tuple: dc.convert_tuple,
}


def display_converter(
    value: Any,
) -> str:
    """
    Convierte un valor Python a su representación
    textual para su visualización en la interfaz.

    Args:
        value (Any):
            Valor a convertir.

    Returns:
        str:
            Representación textual del valor.
    """

    for python_type, converter in DISPLAY_CONVERTERS.items():

        if isinstance(
            value,
            python_type,
        ):
            return converter(value)

    return dc.convert_default(value)


# =============================================================================
# SUPPORT
# =============================================================================


def supports_input_conversion(
    column_type: TypeEngine,
) -> bool:
    """
    Indica si existe un conversor de entrada para
    un tipo SQLAlchemy.

    Args:
        column_type (TypeEngine):
            Tipo SQLAlchemy de la columna.

    Returns:
        bool:
            True si el tipo admite edición desde la
            interfaz; False en caso contrario.
    """

    return any(
        isinstance(
            column_type,
            sqlalchemy_type,
        )
        for sqlalchemy_type in SUPPORTED_INPUT_TYPES
    )

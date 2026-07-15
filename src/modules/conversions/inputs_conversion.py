import json
from decimal import (
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

import modules.conversions.python_converters as pc

SUPPORTED_INPUT_TYPES: dict[type[TypeEngine], Callable[[str], Any]] = {
    Integer: pc.convert_integer,
    Float: pc.convert_float,
    Numeric: pc.convert_numeric,
    String: pc.convert_string,
    Boolean: pc.convert_boolean,
    Date: pc.convert_date,
    DateTime: pc.convert_datetime,
    Time: pc.convert_time,
    Uuid: pc.convert_uuid,
}


def convert(
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

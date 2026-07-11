"""
Entidades que representan el resultado de una
consulta ejecutada.

Permiten almacenar los datos recuperados, la
información necesaria para su edición y el estado
general de la ejecución.

Clases:
    - ResultSet
    - QueryResult
"""

from dataclasses import dataclass
from typing import Any


@dataclass(
    slots=True,
    kw_only=True,
)
class ResultSet:
    """
    Contiene el conjunto de resultados devuelto
    por una consulta.

    Attributes:
        rows (list[list[Any]]):
            Filas obtenidas por la consulta.

        columns (list[str]):
            Nombres de las columnas del resultado.

        columns_types (list[type]):
            Tipos asociados a cada columna.

        table_name (str | None):
            Nombre de la tabla asociada al
            resultado, si existe.

        primary_key_columns (list[str]):
            Columnas que forman la clave primaria
            de la tabla asociada.
    """

    rows: list[list[Any]]
    columns: list[str]
    columns_types: list[type]

    table_name: str | None
    primary_key_columns: list[str]

    @property
    def is_editable(self) -> bool:
        """
        Indica si el conjunto de resultados puede
        modificarse.

        Returns:
            bool:
                - `True` si existe una tabla asociada y
                se dispone de al menos una columna
                de clave primaria.
                - `False` en caso contrario.
        """

        return self.table_name is not None and len(self.primary_key_columns) > 0


@dataclass(
    slots=True,
    kw_only=True,
)
class QueryResult:
    """
    Representa el resultado de la ejecución de una
    consulta.

    Attributes:
        success (bool):
            Indica si la consulta se ejecutó
            correctamente.

        console_output (str):
            Mensajes generados durante la ejecución
            de la consulta.

        result_set (ResultSet | None):
            Conjunto de resultados obtenido por la
            consulta, si existe.
    """

    success: bool
    console_output: str
    result_set: ResultSet | None

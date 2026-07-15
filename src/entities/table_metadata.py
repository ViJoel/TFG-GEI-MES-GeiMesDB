from dataclasses import (
    dataclass,
    field,
)
from typing import Any

from sqlalchemy import Table
from sqlalchemy.types import TypeEngine

from modules.conversions.inputs_conversion import convert


@dataclass(
    slots=True,
    kw_only=True,
)
class TableMetadata:
    """
    Metadatos de una tabla obtenidos mediante
    reflexión con SQLAlchemy.

    Attributes:
        table (Table):
            Objeto `Table` reflejado.

        table_name (str):
            Nombre de la tabla.

        primary_key_columns (list[str]):
            Columnas que forman la clave primaria.

        column_types (dict[str, TypeEngine]):
            Tipos SQLAlchemy asociados a cada
            columna de la tabla.
    """

    table: Table

    table_name: str = field(init=False)

    primary_key_columns: list[str] = field(init=False)

    column_types: dict[str, TypeEngine] = field(init=False)

    def __post_init__(
        self,
    ) -> None:
        """
        Inicializa la información derivada del
        objeto `Table` reflejado.

        Extrae el nombre de la tabla, las columnas
        que forman la clave primaria y el tipo
        SQLAlchemy asociado a cada columna.
        """

        self.table_name = self.table.name

        self.primary_key_columns = [
            column.name for column in self.table.primary_key.columns
        ]

        self.column_types = {column.name: column.type for column in self.table.columns}

    def convert_value(
        self,
        column_name: str,
        value: str,
    ) -> Any:
        """
        Convierte un valor textual al tipo Python
        correspondiente según el tipo SQLAlchemy de
        la columna indicada.

        Args:
            column_name (str):
                Nombre de la columna.

            value (str):
                Valor introducido por el usuario.

        Returns:
            Any:
                Valor convertido al tipo Python
                correspondiente.
        """

        return convert(
            column_type=self.column_types[column_name],
            value=value,
        )

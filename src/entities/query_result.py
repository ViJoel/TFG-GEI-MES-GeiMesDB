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

from entities.table_metadata import TableMetadata


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

        table_metadata (TableMetadata | None):
            Metadatos de la tabla asociada al
            resultado. Será `None` cuando la
            consulta no sea editable.
    """

    rows: list[list[Any]]
    columns: list[str]
    table_metadata: TableMetadata | None

    @property
    def is_editable(
        self,
    ) -> bool:
        """
        Indica si el resultado dispone de metadata
        asociada para permitir operaciones de edición.

        Returns:
            bool:
                True si existe información de la
                tabla asociada; False en caso
                contrario.
        """

        return self.table_metadata is not None

    def supports_editing(
        self,
        column_name: str,
    ) -> bool:
        """
        Indica si una columna puede editarse.

        Args:
            column_name (str):
                Nombre de la columna.

        Returns:
            bool:
                True si la columna admite edición;
                False en caso contrario.
        """

        if self.table_metadata is None:
            return False

        return self.table_metadata.supports_editing(
            column_name=column_name,
        )


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

from dataclasses import dataclass
from typing import Any

from sqlalchemy import update
from sqlalchemy.sql.dml import Update

from entities.table_metadata import TableMetadata


@dataclass(
    slots=True,
    kw_only=True,
)
class UpdateOperation:
    """
    Representa una operación de actualización
    sobre una fila de una tabla.

    Attributes:
        table_name:
            Tabla que será modificada.

        primary_key:
            Valores originales de la clave primaria.

        values:
            Columnas modificadas junto con su nuevo valor.
    """

    table_metadata: TableMetadata

    primary_key: dict[str, Any]

    values: dict[str, Any]

    def to_statement(
        self,
    ) -> Update:
        """
        Construye la sentencia UPDATE equivalente
        utilizando SQLAlchemy Core.

        Returns:
            Update:
                Sentencia preparada para su ejecución.
        """

        table = self.table_metadata.table

        stmt = update(table)

        for column, value in self.primary_key.items():
            stmt = stmt.where(
                table.c[column] == value,
            )

        return stmt.values(**self.values)

    def to_sql(
        self,
        dialect,
    ) -> str:
        """
        Genera la representación SQL de la operación
        utilizando el dialecto especificado.

        Args:
            dialect:
                Dialecto de SQLAlchemy empleado para
                generar la sentencia SQL.

        Returns:
            str:
                Sentencia SQL equivalente a la
                operación de actualización.
        """

        stmt = self.to_statement()

        return str(
            stmt.compile(
                dialect=dialect,
                compile_kwargs={
                    "literal_binds": True,
                },
            )
        )

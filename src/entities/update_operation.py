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

        compiled = stmt.compile(
            dialect=dialect,
        )

        sql = str(compiled)

        # Evitamos `literal_binds=True` y sustituimos
        # manualmente los parámetros para obtener una
        # representación SQL legible incluso cuando
        # algunos valores no pueden compilarse como
        # literales.
        literals = {}

        for key, value in compiled.params.items():

            if isinstance(value, str):
                literals[key] = f"'{value}'"

            elif value is None:
                literals[key] = "NULL"

            else:
                literals[key] = str(value)

        paramstyle = dialect.paramstyle

        if paramstyle == "pyformat":

            for key, literal in literals.items():

                sql = sql.replace(
                    f"%({key})s",
                    literal,
                )

        elif paramstyle == "named":

            for key, literal in literals.items():

                sql = sql.replace(
                    f":{key}",
                    literal,
                )

        elif paramstyle == "format":

            for literal in literals.values():

                sql = sql.replace(
                    "%s",
                    literal,
                    1,
                )

        elif paramstyle == "qmark":

            for literal in literals.values():

                sql = sql.replace(
                    "?",
                    literal,
                    1,
                )

        elif paramstyle == "numeric":

            for index, literal in enumerate(
                literals.values(),
                start=1,
            ):

                sql = sql.replace(
                    f":{index}",
                    literal,
                    1,
                )

        return sql

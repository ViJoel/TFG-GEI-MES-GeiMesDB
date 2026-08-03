from typing import TypedDict

from modules.sql.theme.colors import (
    DEFAULT_COLOR,
    SQL_THEME_COLORS,
)


class SchemaCategory(TypedDict):
    """
    Estructura de una categoría de autocompletado
    basada en el esquema de la base de datos.

    Attributes:
        values:
            Conjunto de identificadores disponibles
            para la categoría.

        color:
            Nombre del color asociado a la categoría
            dentro del tema de la aplicación.
    """

    values: set[str]
    color: str


class SqlSchemaCompletionData:
    """
    Almacena los datos del esquema de la base de
    datos utilizados por el autocompletador SQL.

    Contiene las categorías derivadas del modelo
    del árbol de navegación, como tablas, vistas,
    columnas, restricciones e índices.
    """

    def __init__(self) -> None:
        """
        Inicializa el almacén de datos del esquema
        para el autocompletador.
        """

        self.data = {
            "tables": {
                "values": set(),
            },
            "views": {
                "values": set(),
            },
            "columns": {
                "values": set(),
            },
            "constraints": {
                "values": set(),
            },
            "indexes": {
                "values": set(),
            },
        }

        self._initialize_schema_data()

    def get_data(
        self,
    ) -> dict[str, SchemaCategory]:
        """
        Devuelve una referencia al diccionario
        interno con los datos del esquema del
        autocompletador.

        Returns:
            dict[str, SchemaCategory]:
                Diccionario con las categorías,
                sus valores y metadatos.
        """

        return self.data

    def clear(
        self,
    ) -> None:
        """
        Elimina todos los valores almacenados
        en las categorías del esquema del
        autocompletador.
        """

        for category in self.data.values():
            category["values"].clear()

    def update(
        self,
        completion_data: dict[str, list[str]],
    ) -> None:
        """
        Sustituye los datos actuales del esquema
        por los proporcionados.

        Args:
            completion_data (dict[str, list[str]]):
                Diccionario con las categorías y
                sus respectivos valores obtenidos
                del modelo del árbol.
        """

        self.clear()

        for (
            key,
            values,
        ) in completion_data.items():
            self.data[key]["values"].update(values)

    def _initialize_schema_data(
        self,
    ) -> None:
        """
        Inicializa los metadatos asociados a
        cada categoría del esquema.

        Asigna automáticamente el color de
        representación definido para cada
        categoría.
        """

        for (
            category,
            data,
        ) in self.data.items():
            data["color"] = SQL_THEME_COLORS.get(
                category,
                DEFAULT_COLOR,
            )


SQL_SCHEMA_COMPLETION_DATA = SqlSchemaCompletionData()

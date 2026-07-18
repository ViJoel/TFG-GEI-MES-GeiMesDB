from typing import TypedDict

from modules.sql.theme.colors import (
    DEFAULT_COLOR,
    SQL_THEME_COLORS,
)


class DynamicCategory(TypedDict):
    values: set[str]
    color: str


class SqlDynamicCompletionData:

    def __init__(
        self,
    ) -> None:

        self.data = {
            "parameters": {
                "values": set(),
            },
            "variables": {
                "values": set(),
            },
        }

        self._initialize_dynamic_data()

    def get_data(
        self,
    ) -> dict[str, DynamicCategory]:
        """
        Devuelve una referencia al diccionario
        interno con los datos dinámicos del
        autocompletador.

        Returns:
            dict[str, DynamicCategory]:
                Diccionario con las categorías,
                sus valores y metadatos.
        """

        return self.data

    def clear_dynamic_completion_data(
        self,
    ) -> None:
        """
        Elimina todos los valores almacenados
        en las categorías dinámicas del
        autocompletador.
        """

        for data in self.data.values():
            data["values"].clear()

    def update_dynamic_completion_data(
        self,
        key: str,
        values: set[str],
    ) -> None:
        """
        Añade un conjunto de valores a una
        categoría dinámica del autocompletador.

        Args:
            key (str):
                Categoría que se desea actualizar.

            values (set[str]):
                Valores que se añadirán a la
                categoría indicada.
        """

        self.data[key]["values"].update(values)

    def has_changes(
        self,
        key: str,
        values: set[str],
    ):
        """
        Comprueba si los valores de una categoría
        difieren de los almacenados actualmente.

        Args:
            key (str):
                Categoría que se desea comprobar.

            values (set[str]):
                Valores que se desean comparar.

        Returns:
            bool:
                - `True` si existen diferencias.
                - `False` en caso contrario.
        """

        return values != self.data[key]["values"]

    def _initialize_dynamic_data(
        self,
    ) -> None:
        """
        Inicializa los metadatos asociados a
        cada categoría dinámica.

        Asigna automáticamente el color de
        representación definido para cada
        categoría.
        """

        for category, data in self.data.items():

            # Extrae el color usando el nombre de la clave.
            # Si no existe, usa DEFAULT_COLOR
            data["color"] = SQL_THEME_COLORS.get(
                category,
                DEFAULT_COLOR,
            )

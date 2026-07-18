from modules.sql.theme.colors import (
    DEFAULT_COLOR,
    SQL_THEME_COLORS,
)

SQL_DYNAMIC_COMPLETION_DATA = {
    "identifiers": {
        "values": set(),
    },
    "parameters": {
        "values": set(),
    },
    "variables": {
        "values": set(),
    },
}


def clear_dynamic_completion_data() -> None:
    """
    Elimina todos los valores almacenados
    en las categorías dinámicas del
    autocompletador.
    """

    for data in SQL_DYNAMIC_COMPLETION_DATA.values():
        data["values"].clear()


def update_dynamic_completion_data(
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

    SQL_DYNAMIC_COMPLETION_DATA[key]["values"].update(values)


def has_changes(
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

    return values != SQL_DYNAMIC_COMPLETION_DATA[key]["values"]


def _initialize_dynamic_data() -> None:
    """
    Inicializa los metadatos asociados a
    cada categoría dinámica.

    Asigna automáticamente el color de
    representación definido para cada
    categoría.
    """

    for category, data in SQL_DYNAMIC_COMPLETION_DATA.items():

        # Extrae el color usando el nombre de la clave.
        # Si no existe, usa DEFAULT_COLOR
        data["color"] = SQL_THEME_COLORS.get(
            category,
            DEFAULT_COLOR,
        )

# Ejecutamos la configuración e inyección al cargar el módulo
_initialize_dynamic_data()

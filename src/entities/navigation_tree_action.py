from enum import (
    StrEnum,
    auto,
)


class NavigationTreeAction(StrEnum):
    """
    Define las acciones de alto nivel que pueden solicitarse desde el
    menú contextual del árbol de navegación.

    Estas acciones son emitidas por el menú contextual y consumidas por
    otros componentes de la aplicación, permitiendo desacoplar la lógica
    de generación de SQL de la lógica encargada de mostrarlo o ejecutarlo.
    """

    INSERT_SQL_IN_EDITOR = auto()
    """
    Inserta el SQL generado en el editor sin ejecutarlo.
    """

    EXECUTE_SQL = auto()
    """
    Ejecuta directamente el SQL generado.
    """

from modules.sql.syntax.ansi.functions import SQL_FUNCTIONS
from modules.sql.syntax.ansi.keywords import SQL_KEYWORDS
from modules.sql.syntax.ansi.literals import (
    SQL_BOOLEAN_VALUES,
    SQL_NULL_VALUES,
)
from modules.sql.syntax.ansi.symbols import SQL_SYMBOLS
from modules.sql.syntax.ansi.types import SQL_TYPES
from modules.sql.theme.colors import (
    DEFAULT_COLOR,
    SQL_THEME_COLORS,
)

SQL_STATIC_COMPLETION_DATA = {
    "booleans": {
        "values": SQL_BOOLEAN_VALUES,
    },
    "functions": {
        "values": SQL_FUNCTIONS,
    },
    "keywords": {
        "values": SQL_KEYWORDS,
    },
    "nulls": {
        "values": SQL_NULL_VALUES,
    },
    "types": {
        "values": SQL_TYPES,
    },
}


def _initialize_static_data() -> None:
    """
    Compila automáticamente los patrones
    generados a partir de los valores.
    """

    for category, data in SQL_STATIC_COMPLETION_DATA.items():

        # Extrae el color usando el nombre de la clave.
        # Si no existe, usa DEFAULT_COLOR
        data["color"] = SQL_THEME_COLORS.get(
            category,
            DEFAULT_COLOR,
        )


# Ejecutamos la configuración e inyección al cargar el módulo
_initialize_static_data()

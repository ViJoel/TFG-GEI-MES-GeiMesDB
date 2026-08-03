from enum import (
    Enum,
    auto,
)


class SqlScope(Enum):
    """
    Define el ámbito de ejecución de una consulta SQL.

    Attributes:
        FULL_SCRIPT:
            Ejecuta todo el contenido del editor
            como un único script SQL.

        ACTUAL_QUERY:
            Ejecuta la consulta sobre la que se encuentre
            actualmente el cursor del editor.

        SELECTED_TEXT:
            Ejecuta únicamente el texto actualmente
            seleccionado en el editor.
    """

    ACTUAL_QUERY = auto()
    FULL_SCRIPT = auto()
    SELECTED_TEXT = auto()

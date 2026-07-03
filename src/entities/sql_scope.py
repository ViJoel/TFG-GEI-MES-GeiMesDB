from enum import Enum, auto


class SqlScope(Enum):
    """
    Define el ámbito de ejecución de una consulta SQL.

    Attributes:
        SELECTED_TEXT:
            Ejecuta únicamente el texto actualmente
            seleccionado en el editor.

        FULL_SCRIPT:
            Ejecuta todo el contenido del editor
            como un único script SQL.
    """

    SELECTED_TEXT = auto()
    FULL_SCRIPT = auto()

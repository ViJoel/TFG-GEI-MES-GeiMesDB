"""
Entidades que representan el resultado de la
ejecución de un script.

Permiten almacenar el resultado individual de
cada consulta ejecutada y agruparlos en una única
estructura de resultados.

Clases:
    - ScriptResultItem
    - ScriptResult
"""

from dataclasses import dataclass


@dataclass(
    slots=True,
    kw_only=True,
)
class ScriptResultItem:
    """
    Representa el resultado de la ejecución de una
    consulta individual dentro de un script.

    Attributes:
        query (str):
            Consulta ejecutada.

        error (str | None):
            Mensaje de error producido durante la
            ejecución de la consulta, si existe.
    """

    query: str
    error: str | None = None

    @property
    def success(self) -> bool:
        """
        Indica si la consulta se ejecutó
        correctamente.

        Returns:
            bool:
                - `True` si no se produjo ningún error;
                - `False` en caso contrario.
        """

        return self.error is None


@dataclass(
    slots=True,
    kw_only=True,
)
class ScriptResult:
    """
    Contiene los resultados de la ejecución
    de un script SQL.

    Attributes:
        items (list[ScriptResultItem]):
            Resultados individuales de las
            consultas ejecutadas.
    """

    items: list[ScriptResultItem]

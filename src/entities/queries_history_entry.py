from dataclasses import (
    dataclass,
    field,
)
from datetime import (
    datetime,
    timezone,
)


# slots: Optimiza memoria y restringe atributos fijos.
# kw_only: Fuerza la inicialización explícita mediante nombres de argumentos.
@dataclass(
    slots=True,
    kw_only=True,
)
class QueriesHistoryEntry:
    """
    Representa una entrada individual en el historial de consultas de la aplicación.

    Mapea directamente una fila de la tabla 'queries_history' en la base de datos.

    Attributes:
        connection_id (str): Identificador único de la conexión utilizada.
        query (str): El texto completo de la consulta SQL ejecutada.
        executed_at (datetime): Fecha y hora de ejecución en formato UTC.
    """

    connection_id: str = ""
    query: str = ""
    executed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

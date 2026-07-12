from datetime import datetime

from entities.connection import Connection
from entities.queries_history_entry import QueriesHistoryEntry
from modules.queries_history.model import get_queries_history as gqh
from modules.queries_history.model import save_queries_history_batch as sqhb


def save_queries_history_batch(
    connection: Connection,
    entries: list[QueriesHistoryEntry],
) -> None:
    """
    Orquesta la inserción masiva de entradas del historial
    de consultas delegando la operación en la capa de datos.

    Args:
        connection (Connection):
            Objeto de la conexión.

        entries (list[QueriesHistoryEntry]):
            Lista con las nuevas entradas
            del historial de consultas.
    """

    return sqhb(
        connection=connection,
        entries=entries,
    )


def get_queries_history(
    connection: Connection,
    start: datetime,
    end: datetime,
) -> list[QueriesHistoryEntry]:
    """
    Solicita el historial de consultas filtrado por rango
    de fechas para una conexión específica.

    Args:
        connection (Connection):
            Objeto de la conexión.

        start (datetime):
            Fecha de inicio del rango.

        end (datetime):
            Fecha de fin del rango.

    Returns:
        list[QueriesHistoryEntry]:
            Lista de entidades con el historial de consultas
            encontrado.
    """

    return gqh(
        connection=connection,
        start=start,
        end=end,
    )

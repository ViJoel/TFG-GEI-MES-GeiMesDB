import sqlite3
from datetime import datetime

from entities.connection import Connection
from entities.queries_history_entry import QueriesHistoryEntry
from log.app_logger import get_logger
from modules.database.model import get_connection as get_db_connection
from modules.database.wrapper import handle_db_errors

logger = get_logger(__name__)


def _map_row_to_entry(row: sqlite3.Row) -> QueriesHistoryEntry:
    """
    Reconstruye una entidad QueriesHistoryEntry
    a partir de una fila SQLite.

    Args:
        row (sqlite3.Row):
            Registro recuperado desde la base de datos.

    Returns:
        QueriesHistoryEntry:
            Entidad de entrada del historial reconstruida.
    """

    return QueriesHistoryEntry(
        connection_id=row["connection_id"],
        query=row["query"],
        executed_at=datetime.fromisoformat(row["executed_at"]),
    )


@handle_db_errors("crear entrada del historial de consultas")
def save_queries_history_batch(
    connection: Connection,
    entries: list[QueriesHistoryEntry],
) -> None:
    """
    Inserta una lista completa de entradas
    del historial de consultas en una sola
    operación de disco.

    Args:
        connection (Connection):
            Objeto de la conexión.

        entries (list[QueriesHistoryEntry]):
            Lista con las nuevas entradas
            del historial de consultas.
    """

    logger.info(
        "Saving queries history entries for connection "
        f"'{connection.name}' (ID: {connection.id})..."
    )

    query = """
    INSERT INTO queries_history (
        connection_id, query, executed_at
    ) VALUES (?, ?, ?)
    """

    with get_db_connection() as conn:

        cur = conn.cursor()

        # Convertimos la lista de objetos a una lista de tuplas que SQLite entiende
        payload = [
            (
                e.connection_id,
                e.query,
                e.executed_at.isoformat(),
            )
            for e in entries
        ]

        # SQLite procesa toda la lista internamente a máxima velocidad
        cur.executemany(
            query,
            payload,
        )

    logger.success(
        f"Queries history entries saved for connection '{connection.name}' (ID: {connection.id})."
    )


@handle_db_errors("obtener historial de consultas")
def get_queries_history(
    connection: Connection,
    start: datetime,
    end: datetime,
) -> list[QueriesHistoryEntry]:
    """
    Recupera el historial de consultas
    filtrado por rango de fechas desde
    el disco.

    Args:
        connection (Connection):
            Objeto de la conexión.

        start (datetime):
            Fecha de inicio.

        end (datetime):
            Fecha de fin.
    """

    start_date = start.isoformat()
    end_date = end.isoformat()

    logger.info(
        "Getting history of connection "
        f"'{connection.name}' (ID: {connection.id})"
        f"from {start_date} to {end_date}"
        "..."
    )

    query = """
        SELECT connection_id, query, executed_at
        FROM queries_history
        WHERE connection_id = ? AND executed_at BETWEEN ? AND ?
        ORDER BY executed_at DESC
        """

    entries_list: list[QueriesHistoryEntry] = []

    with get_db_connection() as conn:

        cur = conn.cursor()

        cur.execute(
            query,
            (
                connection.id,
                start.isoformat(),
                end.isoformat(),
            ),
        )

        rows = cur.fetchall()

        for row in rows:
            entries_list.append(_map_row_to_entry(row))

    logger.success(f"Loaded {len(entries_list)} queries history entries.")

    return entries_list

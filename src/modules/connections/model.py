import logging
import sqlite3

from entities.connection import Connection
from entities.driver import Driver
from modules.database.model import get_connection as get_db_connection
from modules.database.wrapper import handle_db_errors

logger = logging.getLogger(__name__)


def _map_row_to_connection(row: sqlite3.Row) -> Connection:
    """
    Reconstruye una entidad Connection a partir
    de una fila SQLite.

    Args:
        row (sqlite3.Row):
            Registro recuperado desde la base de datos.

    Returns:
        Connection:
            Entidad de conexión reconstruida.
    """

    return Connection(
        id=row["id"],
        name=row["name"],
        driver=Driver(row["driver"]),
        host=row["host"],
        port=row["port"],
        database=row["database"],
        username=row["username"],
        password=row["password"],
        path=row["path"],
    )


@handle_db_errors("cargar todas las conexiones")
def get_all_connections() -> list[Connection]:
    """
    Recupera todas las conexiones persistidas
    ordenadas alfabéticamente por nombre.

    Returns:
        list[Connection]:
            Lista de conexiones registradas.
    """

    query = """
    SELECT *
    FROM connections
    ORDER BY name ASC
    """

    connections_list: list[Connection] = []

    with get_db_connection() as conn:

        cur = conn.cursor()

        cur.execute(query)

        rows = cur.fetchall()

        for row in rows:
            connections_list.append(_map_row_to_connection(row))

    logger.info(
        f"Conexiones recuperadas con éxito ({len(connections_list)} registros)."
    )

    return connections_list


@handle_db_errors("crear conexión")
def create_connection(connection: Connection) -> None:
    """
    Persiste una nueva conexión en la base de datos.

    Args:
        connection (Connection):
            Conexión a registrar.
    """

    query = """
    INSERT INTO connections (
        id, name, driver, host, port, database, username, password, path
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    with get_db_connection() as conn:

        cur = conn.cursor()

        cur.execute(
            query,
            (
                connection.id,
                connection.name,
                connection.driver.value,
                connection.host,
                connection.port,
                connection.database,
                connection.username,
                connection.password,
                connection.path,
            ),
        )

    logger.info(f"Conexión '{connection.name}' (ID: {connection.id}) creada con éxito.")


@handle_db_errors("actualizar conexión")
def update_connection(connection: Connection) -> None:
    """
    Actualiza una conexión persistida existente.

    Args:
        connection (Connection):
            Conexión con los datos actualizados.
    """

    query = """
    UPDATE connections
    SET
        name = ?,
        driver = ?,
        host = ?,
        port = ?,
        database = ?,
        username = ?,
        password = ?,
        path = ?
    WHERE id = ?
    """

    with get_db_connection() as conn:

        cur = conn.cursor()

        cur.execute(
            query,
            (
                connection.name,
                connection.driver.value,
                connection.host,
                connection.port,
                connection.database,
                connection.username,
                connection.password,
                connection.path,
                connection.id,
            ),
        )

        # No existe ninguna conexión con ese ID.
        if cur.rowcount == 0:
            logger.warning(
                f"Conexión '{connection.name}' (ID: {connection.id}) no encontrada para actualizar."
            )
            return

    logger.info(
        f"Conexión '{connection.name}' (ID: {connection.id}) actualizada con éxito."
    )


@handle_db_errors("eliminar conexión")
def delete_connection(connection: Connection) -> None:
    """
    Elimina una conexión persistida.

    Args:
        connection (Connection):
            Conexión a eliminar.
    """

    query = """
    DELETE FROM connections
    WHERE id = ?
    """

    with get_db_connection() as conn:

        cur = conn.cursor()

        cur.execute(
            query,
            (connection.id,),
        )

        # No existe ninguna conexión con ese ID.
        if cur.rowcount == 0:
            logger.warning(
                f"Conexión '{connection.name}' (ID: {connection.id}) no encontrada para eliminar."
            )
            return

    logger.info(
        f"Conexión '{connection.name}' (ID: {connection.id}) eliminada con éxito."
    )


@handle_db_errors("verificar existencia de conexión")
def connection_exists(connection_id: str) -> bool:
    """
    Verifica si existe una conexión registrada
    con el identificador especificado.

    Args:
        connection_id (str):
            Identificador único de la conexión.

    Returns:
        bool:
            True si la conexión existe,
            False en caso contrario.
    """

    query = """
    SELECT 1
    FROM connections
    WHERE id = ?
    LIMIT 1
    """

    with get_db_connection() as conn:

        cur = conn.cursor()

        cur.execute(query, (connection_id,))

        exists = cur.fetchone() is not None

    logger.info(
        f"Verificación de existencia para conexión ID '{connection_id}': {exists}"
    )

    return exists

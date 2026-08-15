import sqlite3

from entities.connection import Connection
from entities.driver import Driver
from log.app_logger import get_logger
from modules.connections.crypto import (
    decrypt,
    encrypt,
)
from modules.database.model import get_connection as get_db_connection
from modules.database.wrapper import handle_db_errors

logger = get_logger(__name__)


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

    logger.info("Loading persisted connections...")

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
            connections_list.append(
                decrypt(
                    _map_row_to_connection(row),
                ),
            )

    logger.success(f"Loaded {len(connections_list)} persisted connections.")

    return connections_list


@handle_db_errors("crear conexión")
def create_connection(connection: Connection) -> None:
    """
    Persiste una nueva conexión en la base de datos.

    Args:
        connection (Connection):
            Conexión a registrar.
    """

    logger.info(f"Creating connection '{connection.name}'...")

    query = """
    INSERT INTO connections (
        id, name, driver, host, port, database, username, password, path
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    # Se crea una copia cifrada para persistirla.
    # La instancia original permanece intacta.
    encrypted_connection = encrypt(connection)

    with get_db_connection() as conn:

        cur = conn.cursor()

        cur.execute(
            query,
            (
                encrypted_connection.id,
                encrypted_connection.name,
                encrypted_connection.driver.value,
                encrypted_connection.host,
                encrypted_connection.port,
                encrypted_connection.database,
                encrypted_connection.username,
                encrypted_connection.password,
                encrypted_connection.path,
            ),
        )

    logger.success(f"Connection '{connection.name}' created (ID: {connection.id}).")


@handle_db_errors("actualizar conexión")
def update_connection(connection: Connection) -> None:
    """
    Actualiza una conexión persistida existente.

    Args:
        connection (Connection):
            Conexión con los datos actualizados.
    """

    logger.info(f"Updating connection '{connection.name}' (ID: {connection.id})...")

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

    # Se crea una copia cifrada para persistirla.
    # La instancia original permanece intacta.
    encrypted_connection = encrypt(connection)

    with get_db_connection() as conn:

        cur = conn.cursor()

        cur.execute(
            query,
            (
                encrypted_connection.name,
                encrypted_connection.driver.value,
                encrypted_connection.host,
                encrypted_connection.port,
                encrypted_connection.database,
                encrypted_connection.username,
                encrypted_connection.password,
                encrypted_connection.path,
                encrypted_connection.id,
            ),
        )

        # No existe ninguna conexión con ese ID.
        if cur.rowcount == 0:
            logger.warning(
                f"Connection '{connection.name}' (ID: {connection.id}) not found."
            )
            return

    logger.success(f"Connection '{connection.name}' (ID: {connection.id}) updated.")


@handle_db_errors("eliminar conexión")
def delete_connection(connection: Connection) -> None:
    """
    Elimina una conexión persistida.

    Args:
        connection (Connection):
            Conexión a eliminar.
    """

    logger.info(f"Deleting connection '{connection.name}' (ID: {connection.id})...")

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
                f"Connection '{connection.name}' (ID: {connection.id}) not found."
            )
            return

    logger.success(f"Connection '{connection.name}' (ID: {connection.id}) deleted.")


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

    logger.debug(f"Connection existence check: id={connection_id}, exists={exists}")

    return exists

import logging

from model.database.model import get_connection as get_db_connection
from model.database.wrapper import handle_db_errors
from model.entities.connection import Connection
from model.entities.driver import Driver

# Crear sub-logger
logger = logging.getLogger(__name__)


def _map_row_to_connection(row) -> Connection:

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


# TODO: PythonDoc
@handle_db_errors("cargar todas las conexiones")
def get_all_connections() -> list[Connection]:

    query = "SELECT * FROM connections ORDER BY name ASC"
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


# TODO: PythonDoc
@handle_db_errors("crear conexión")
def create_connection(connection: Connection) -> None:

    # Consulta SQL para insertar una nueva conexión
    query = """
    INSERT INTO connections (
        id, name, driver, host, port, database, username, password, path
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    # Abre conexión a la base de datos usando un context manager
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

        logger.info(
            f"Conexión '{connection.name}' (ID: {connection.id}) creada con éxito."
        )


# TODO: PythonDoc
@handle_db_errors("actualizar conexión")
def update_connection(connection: Connection) -> None:

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

        if cur.rowcount == 0:
            logger.warning(
                f"Conexión '{connection.name}' (ID: {connection.id}) no encontrada para actualizar."
            )
            return

        logger.info(
            f"Conexión '{connection.name}' (ID: {connection.id}) actualizada con éxito."
        )


# TODO: PythonDoc
@handle_db_errors("eliminar conexión")
def delete_connection(connection: Connection) -> None:

    query = """
    delete from connections
    where id = ?
    """

    with get_db_connection() as conn:
        cur = conn.cursor()

        cur.execute(
            query,
            (connection.id,),
        )

        if cur.rowcount == 0:
            logger.warning(
                f"Conexión '{connection.name}' (ID: {connection.id}) no encontrada para eliminar."
            )
            return

        logger.info(
            f"Conexión '{connection.name}' (ID: {connection.id}) eliminada con éxito."
        )

import logging
from .connection import Connection
from model.database.database import (
    get_connection as get_db_connection,
)
from model.database.wrapper import handle_db_errors

# Crear sub-logger
logger = logging.getLogger(__name__)


# TODO: Añadir PythonDoc a esta función
@handle_db_errors("cargar todas las conexiones")
def get_all_connections() -> list[Connection]:
    """
    Recupera todas las conexiones de la base de datos.

    Returns:
        list[Connection]: Lista de objetos Connection (vacía si no hay registros).
    """

    query = "select * from connections order by name asc"
    connections_list = []

    return


# TODO: Revisar el PythonDoc de esta función
@handle_db_errors("crear conexión")
def create_connection(connection: Connection) -> bool:
    """
    Inserta una nueva conexión en la base de datos.

    Args:
        connection: Objeto Connection con los datos a insertar.

    Returns:
        bool: True si la inserción fue exitosa.

    Raises:
        IntegrityError: Si el ID ya existe en la base de datos.
        OperationalError: Si la base de datos no está accesible.
        Exception: Para cualquier otro error inesperado de SQLite.
    """

    # Consulta SQL para insertar una nueva conexión
    query = """
    insert into connections (
        id, name, driver, host, port, database, username, password, path
    ) values (?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        conn.commit()
        logger.info(
            f"Conexión '{connection.name}' (ID: {connection.id}) creada con éxito."
        )
        return True


# TODO: Añadir PythonDoc a esta función
@handle_db_errors("actualizar conexión")
def update_connection(connection: Connection) -> bool:
    query = """
    update connections
    set
        name = ?,
        driver = ?,
        host = ?,
        port = ?,
        database = ?,
        username = ?,
        password = ?,
        path = ?
    where id = ?
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
        conn.commit()
        logger.info(
            f"Conexión '{connection.name}' (ID: {connection.id}) actualizada con éxito."
        )
        return True


# TODO: Añadir PythonDoc a esta función
@handle_db_errors("eliminar conexión")
def delete_connection(connection: Connection) -> bool:
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
        conn.commit()
        logger.info(
            f"Conexión '{connection.name}' (ID: {connection.id}) eliminada con éxito."
        )
        return True

import logging
from model.connections.connection import Connection
from model.connections.database import (
    init_database,
    get_connection as get_db_connection,
)
from sqlite3 import IntegrityError, OperationalError

# Crear sub-logger
logger = logging.getLogger(__name__)

def create_connections_database():
    """Crea la base de datos de conexiones."""
    init_database()


def create_connection(connection: Connection) -> bool:
    """Inserta una nueva conexión en la base de datos.

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
        try:
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
            logger.info(f"Conexión '{connection.name}' (ID: {connection.id}) creada con éxito.")
            return True

        except IntegrityError as e:
            logger.warning(f"Intento de duplicar ID: {connection.id}. Error: {e}")
            raise
        except OperationalError as e:
            logger.error(f"Error de acceso a la base de datos (¿Existe el archivo?): {e}")
            raise
        except Exception as e:
            logger.error(f"Error inesperado al crear conexión: {e}")
            raise

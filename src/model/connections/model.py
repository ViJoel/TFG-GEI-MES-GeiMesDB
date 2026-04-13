from model.connections.connection import Connection
from model.connections.database import (
    init_database,
    get_connection as get_db_connection,
)
from model.connections.drivers import Driver


def create_connections_database():
    """Crea la base de datos de conexiones."""
    init_database()


def create_connection(connection: Connection) -> int:
    """Crea una conexión."""

    # Consulta SQL para insertar una nueva conexión
    query = """
    insert into connections (
        name, driver, host, port, database, username, password, path
    ) values (?, ?, ?, ?, ?, ?, ?, ?)
    """

    # Abre conexión a la base de datos usando un context manager
    with get_db_connection() as conn:

        # Crea un cursor para ejecutar la consulta
        cursor = conn.cursor()

        # Ejecuta el INSERT con los valores de la conexión
        cursor.execute(
            query,
            (
                connection.name,
                connection.driver.value,  # Convierte el enum a string
                connection.host,
                connection.port,
                connection.database,
                connection.username,
                connection.password,
                connection.path,
            ),
        )

        # Guarda los cambios en la base de datos
        conn.commit()

        # Devuelve el id generado automáticamente
        return cursor.lastrowid


def update_connection():
    """Edita una conexión."""
    return


def delete_connection():
    """Elimina una conexión."""
    return


def get_all_connections():
    """Obtiene todas las conexiones."""
    return

import logging

from model.connections.connection import Connection
from model.connections.driver import Driver
from model.database.model import get_connection as get_db_connection
from model.database.wrapper import handle_db_errors

# Crear sub-logger
logger = logging.getLogger(__name__)


def _map_row_to_connection(row) -> Connection:
    """
    Convierte una fila retornada por SQLite en una instancia del modelo
    de dominio ``Connection``.

    Esta función actúa como un mapper interno entre la representación
    persistida en la base de datos y el objeto utilizado por la lógica
    de negocio de la aplicación.

    El campo ``driver`` almacenado como texto en SQLite se transforma
    automáticamente en un miembro del enumerado :class:`Driver`.

    Args:
        row (sqlite3.Row):
            Fila obtenida desde un cursor SQLite configurado con
            ``sqlite3.Row`` como ``row_factory``.

    Returns:
        Connection:
            Instancia completamente inicializada del modelo ``Connection``.

    Raises:
        IndexError:
            Si la fila no contiene alguna de las columnas esperadas.

        ValueError:
            Si el valor almacenado en la columna ``driver`` no corresponde
            a un valor válido del enumerado ``Driver``.
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


# TODO: Añadir PythonDoc a esta función
@handle_db_errors("cargar todas las conexiones")
def get_all_connections() -> list[Connection]:
    """
    Recupera todas las conexiones almacenadas en la base de datos.

    Las conexiones se retornan ordenadas alfabéticamente por el campo
    ``name`` para facilitar su visualización en la interfaz de usuario.

    Esta operación es de solo lectura y no modifica el estado de la base
    de datos.

    Returns:
        list[Connection]:
            Lista de objetos ``Connection`` persistidos en la base de datos.

            - Retorna una lista vacía si no existen registros.
            - El orden de los elementos es ascendente por nombre.

    Raises:
        sqlite3.OperationalError:
            Si ocurre un problema de acceso a la base de datos.

        sqlite3.DatabaseError:
            Si SQLite detecta un error interno durante la consulta.

        Exception:
            Cualquier excepción no controlada propagada desde la capa
            de persistencia.
    """

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


# TODO: Revisar el PythonDoc de esta función
@handle_db_errors("crear conexión")
def create_connection(connection: Connection) -> bool:
    """
    Inserta una nueva conexión en la base de datos.

    La operación persiste todos los parámetros técnicos asociados a una
    conexión de base de datos, incluyendo credenciales, host, puerto
    y configuración específica del driver.

    El identificador único (UUID) de la conexión debe ser válido y no
    existir previamente en la tabla ``connections``.

    Args:
        connection (Connection):
            Objeto ``Connection`` con los datos que se desean persistir.

    Returns:
        bool:
            ``True`` si la inserción se realizó correctamente.

    Raises:
        sqlite3.IntegrityError:
            Si ya existe una conexión con el mismo identificador o se viola
            alguna restricción de integridad definida en el esquema.

        sqlite3.OperationalError:
            Si ocurre un fallo operativo al acceder a la base de datos.

        sqlite3.DatabaseError:
            Si SQLite detecta un error interno durante la operación.

        Exception:
            Cualquier excepción inesperada propagada desde la capa de
            persistencia.
    """

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

        return True


# TODO: Añadir PythonDoc a esta función
@handle_db_errors("actualizar conexión")
def update_connection(connection: Connection) -> bool:
    """
    Actualiza una conexión existente en la base de datos.

    La actualización se realiza utilizando el identificador único
    ``id`` de la conexión como criterio de búsqueda.

    Todos los campos configurables de la conexión son sobrescritos
    con los valores contenidos en el objeto recibido.

    Args:
        connection (Connection):
            Instancia ``Connection`` con los nuevos valores a persistir.

    Returns:
        bool:
            ``True`` si la actualización se ejecutó correctamente.

    Raises:
        sqlite3.IntegrityError:
            Si la operación viola restricciones de integridad.

        sqlite3.OperationalError:
            Si ocurre un fallo de acceso a la base de datos.

        sqlite3.DatabaseError:
            Si SQLite detecta un error interno durante la operación.

        Exception:
            Cualquier excepción no controlada propagada desde la capa
            de persistencia.
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

        if cur.rowcount == 0:
            logger.warning(
                f"Conexión '{connection.name}' (ID: {connection.id}) no encontrada para actualizar."
            )
            return False

        logger.info(
            f"Conexión '{connection.name}' (ID: {connection.id}) actualizada con éxito."
        )

        return True


@handle_db_errors("eliminar conexión")
def delete_connection(connection: Connection) -> bool:
    """
    Elimina una conexión persistida en la base de datos.

    La eliminación se realiza utilizando el identificador único
    ``id`` de la conexión recibida.

    Esta operación es irreversible y removerá permanentemente el
    registro asociado de la tabla ``connections``.

    Args:
        connection (Connection):
            Objeto ``Connection`` que representa la conexión a eliminar.

    Returns:
        bool:
            ``True`` si la eliminación se ejecutó correctamente.

    Raises:
        sqlite3.IntegrityError:
            Si existen restricciones de integridad que impiden la eliminación.

        sqlite3.OperationalError:
            Si ocurre un problema de acceso a la base de datos.

        sqlite3.DatabaseError:
            Si SQLite detecta un error interno durante la operación.

        Exception:
            Cualquier excepción inesperada propagada desde la capa
            de persistencia.
    """

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
            return False

        logger.info(
            f"Conexión '{connection.name}' (ID: {connection.id}) eliminada con éxito."
        )

        return True

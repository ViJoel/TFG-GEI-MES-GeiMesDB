from entities.connection import Connection
from modules.connections.model import connection_exists as ce
from modules.connections.model import create_connection as cc
from modules.connections.model import delete_connection as dc
from modules.connections.model import get_all_connections as gac
from modules.connections.model import update_connection as uc


def get_connections() -> list[Connection]:
    """
    Recupera todas las conexiones persistidas.

    Returns:
        list[Connection]:
            Lista de conexiones registradas.
    """

    return gac()


def create_connection(connection: Connection) -> None:
    """
    Crea una nueva conexión persistida.

    Args:
        connection (Connection):
            Conexión a registrar.
    """

    return cc(connection=connection)


def update_connection(connection: Connection) -> None:
    """
    Actualiza una conexión persistida existente.

    Args:
        connection (Connection):
            Conexión con los datos actualizados.
    """

    return uc(connection=connection)


def delete_connection(connection: Connection) -> None:
    """
    Elimina una conexión persistida.

    Args:
        connection (Connection):
            Conexión a eliminar.
    """

    return dc(connection=connection)


def connection_exists(connection_id: str) -> bool:
    """
    Verifica si existe una conexión registrada.

    Args:
        connection_id (str):
            Identificador único de la conexión.

    Returns:
        bool:
            True si la conexión existe,
            False en caso contrario.
    """

    return ce(connection_id=connection_id)

from model.connections.model import create_connection as cc
from model.connections.model import delete_connection as dc
from model.connections.model import get_all_connections as gac
from model.entities.connection import Connection


def get_connections() -> list[Connection]:
    """
    Recupera todas las conexiones disponibles desde la capa modelo.

    Returns:
        list[Connection]:
            Lista de conexiones persistidas en la base de datos.
    """

    return gac()


def create_connection(connection: Connection) -> bool:
    return cc(connection=connection)


def delete_connection(connection: Connection) -> bool:
    return dc(connection=connection)

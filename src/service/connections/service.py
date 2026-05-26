from model.connections.model import create_connection as cc
from model.connections.model import update_connection as uc
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


# TODO: PythonDoc
def create_connection(connection: Connection) -> None:
    return cc(connection=connection)


# TODO: PythonDoc
def update_connection(connection: Connection) -> None:
    return uc(connection=connection)


# TODO: PythonDoc
def delete_connection(connection: Connection) -> None:
    return dc(connection=connection)

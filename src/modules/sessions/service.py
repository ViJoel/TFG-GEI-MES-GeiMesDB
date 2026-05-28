from entities.connection import Connection
from modules.sessions.manager import close_all_sessions as cas
from modules.sessions.manager import close_session as cs
from modules.sessions.manager import get_session as gs
from modules.sessions.manager import has_session as hs
from modules.sessions.manager import open_session as os
from modules.sessions.manager import test_connection as tc
from modules.sessions.session import Session


def open_session(connection: Connection) -> Session:
    """
    Abre una nueva sesión activa.

    Args:
        connection (Connection):
            Configuración persistida.

    Returns:
        Session:
            Sesión activa creada.
    """

    return os(connection)


def close_session(connection_id: str) -> None:
    """
    Cierra una sesión activa.

    Args:
        connection_id (str):
            Identificador único de la conexión.
    """

    cs(connection_id)


def get_session(connection_id: str) -> Session | None:
    """
    Recupera una sesión activa.

    Args:
        connection_id (str):
            Identificador único de la conexión.

    Returns:
        Session | None:
            Sesión encontrada o None.
    """

    return gs(connection_id)


def has_session(connection_id: str) -> bool:
    """
    Verifica si existe una sesión activa.

    Args:
        connection_id (str):
            Identificador único de la conexión.

    Returns:
        bool:
            - `True` si existe sesión activa.
    """

    return hs(connection_id)


def close_all_sessions() -> None:
    """
    Cierra todas las sesiones activas.
    """

    cas()


def test_connection(connection: Connection) -> bool:
    """
    Verifica conectividad de una sesión activa.

    Args:
        connection_id (str):
            Identificador único de la conexión.

    Returns:
        bool:
            - `True` si la conexión responde correctamente.
    """

    return tc(connection)

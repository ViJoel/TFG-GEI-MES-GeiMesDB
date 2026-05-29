import logging

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from entities.connection import Connection
from modules.sessions.session import Session

logger = logging.getLogger(__name__)

# Registro global de sesiones activas.
#
# Key:
#     ID de conexión persistida.
#
# Value:
#     Session activa asociada.
_active_sessions: dict[str, Session] = {}


def open_session(connection: Connection) -> Session:
    """
    Crea y registra una nueva sesión activa.

    Args:
        connection (Connection):
            Configuración persistida utilizada
            para abrir la sesión.

    Returns:
        Session:
            Sesión activa creada.

    Raises:
        ValueError:
            Si ya existe una sesión activa
            para la conexión especificada.
    """

    # Evita múltiples sesiones activas
    # para la misma conexión persistida.
    if connection.id in _active_sessions:
        raise ValueError(f"There is already an active session for '{connection.name}'.")

    logger.info(f"Opening session for '{connection.name}'...")

    # Crear sesión runtime.
    session = Session.create(connection)

    # Registrar sesión activa.
    _active_sessions[connection.id] = session

    logger.info(f"Session opened correctly for '{connection.name}'.")

    return session


def close_session(connection_id: str) -> None:
    """
    Cierra y elimina una sesión activa.

    Args:
        connection_id (str):
            Identificador único de la conexión.
    """

    # Recuperar sesión activa.
    session = get_session(connection_id)

    # No existe sesión activa.
    if session is None:
        logger.warning(f"There is no active session for the connection {connection_id}.")
        return

    logger.info(f"Closing session for '{session.connection.name}'...")

    # Liberar recursos SQLAlchemy.
    session.close()

    # Eliminar registro runtime.
    del _active_sessions[connection_id]

    logger.info(f"Sesión cerrada correctamente para '{session.connection.name}'.")


def get_session(
    connection_id: str,
) -> Session | None:
    """
    Recupera una sesión activa registrada.

    Args:
        connection_id (str):
            Identificador único de la conexión.

    Returns:
        Session | None:
            Sesión activa encontrada o None si no existe.
    """

    return _active_sessions.get(connection_id)


def has_session(connection_id: str) -> bool:
    """
    Verifica si existe una sesión activa
    para la conexión especificada.

    Args:
        connection_id (str):
            Identificador único de la conexión.

    Returns:
        bool:
            - `True` si existe una sesión activa.
            - `False` en caso contrario.
    """

    return connection_id in _active_sessions


def close_all_sessions() -> None:
    """
    Cierra todas las sesiones activas
    registradas en memoria.
    """

    logger.info("Closing all active sessions...")

    # Crear copia para evitar modificar
    # el diccionario durante iteración.
    connection_ids = list(_active_sessions.keys())

    for connection_id in connection_ids:
        close_session(connection_id)

    logger.info("All active sessions were closed.")


def test_connection(connection: Connection) -> bool:
    """
    Verifica si una conexión puede comunicarse
    correctamente con la base de datos asociada.

    Args:
        connection (Connection):
            Configuración persistida utilizada
            para probar la conexión.

    Returns:
        bool:
            - `True` si la conexión responde correctamente.
            - `False` en caso contrario.
    """

    logger.info(f"Testing connection for '{connection.name}'...")

    session = None

    try:

        # Crear sesión temporal.
        session = Session.create(connection)

        with session.engine.connect() as conn:

            # Oracle requiere DUAL.
            if connection.driver.name == "ORACLE":
                query = "SELECT 1 FROM DUAL"
            else:
                query = "SELECT 1"

            conn.execute(text(query))

        logger.info(f"Connection test successful for '{connection.name}'.")

        return True

    except SQLAlchemyError as e:

        logger.error(f"Error verifying connection '{connection.name}': {e}.")

        return False

    finally:

        # Liberar recursos aunque falle.
        if session is not None:
            session.close()

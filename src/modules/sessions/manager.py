import logging

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from entities.connection import Connection
from entities.driver import Driver
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

    if connection.id in _active_sessions:

        logger.error(
            f"Cannot open session for '{connection.name}'. "
            f"An active session already exists."
        )

        raise ValueError(f"There is already an active session for '{connection.name}'.")

    logger.info(f"Opening session for '{connection.name}'...")

    session = None

    try:

        logger.info(f"Creating runtime session for '{connection.name}'...")

        session = Session.create(connection)

        logger.success(f"Runtime session created for '{connection.name}'.")

        logger.info(f"Verifying connection to '{connection.name}'...")

        with session.engine.connect() as conn:

            query = (
                "SELECT 1 FROM DUAL"
                if connection.driver == Driver.ORACLE
                else "SELECT 1"
            )

            conn.execute(text(query))

        logger.success(f"Connection verified for '{connection.name}'.")

        logger.info(f"Registering active session for '{connection.name}'...")

        _active_sessions[connection.id] = session

        logger.success(f"Active session registered for '{connection.name}'.")

        logger.success(f"Session opened for '{connection.name}'.")

        return session

    except Exception as e:

        logger.error(
            f"Failed to open session for '{connection.name}'. " f"Exception: {e}"
        )

        if session is not None:
            try:
                session.close()
            except Exception:
                pass

        raise


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
        logger.warning(
            f"There is no active session for the connection {connection_id}."
        )
        return

    logger.info(f"Closing session for '{session.connection.name}'...")

    session.close()

    logger.info(f"Removing active session registry for '{session.connection.name}'...")

    del _active_sessions[connection_id]

    logger.success(f"Active session registry removed for '{session.connection.name}'.")

    logger.success(f"Session closed correctly for '{session.connection.name}'.")


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

    logger.success("All active sessions were closed.")


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
            if connection.driver == Driver.ORACLE:
                query = "SELECT 1 FROM DUAL"
            else:
                query = "SELECT 1"

            conn.execute(text(query))

        logger.success(f"Connection test successful for '{connection.name}'.")

        return True

    except SQLAlchemyError as e:

        logger.error(
            f"Connection test failed for '{connection.name}'. " f"Exception: {e}"
        )

        return False

    finally:

        logger.info(f"Releasing temporary resources for '{connection.name}'...")

        # Liberar recursos aunque falle.
        if session is not None:
            session.close()

        logger.success(f"Temporary resources released for '{connection.name}'.")

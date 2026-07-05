from entities.connection import Connection
from log.app_logger import get_logger

logger = get_logger(__name__)

_selected_connection: Connection | None = None


def set_selected_connection(
    connection: Connection | None,
) -> None:
    """
    Actualiza la conexión seleccionada.

    Args:
        connection (Connection):
            Objeto de la conexión.
    """

    global _selected_connection

    _selected_connection = connection

    if _selected_connection is None:
        logger.debug("Global state updated: _selected_connection = None")
    else:
        logger.debug(
            f"Global state updated: "
            f"_selected_connection = '{_selected_connection.name}' "
            f"(ID: {_selected_connection.id})"
        )


def get_selected_connection() -> Connection | None:
    """
    Retorna la conexión seleccionada.

    Returns:
        Connection | None:
            Objeto de la conexión.
    """

    return _selected_connection

from typing import Any

from entities.connection import Connection
from entities.driver import Driver
from entities.query_result import QueryResult
from entities.script_result import ScriptResult
from entities.session import Session
from entities.update_operation import UpdateOperation
from modules.sessions.db_tree import get_db_tree as gdt
from modules.sessions.manager import close_all_sessions as cas
from modules.sessions.manager import close_session as cs
from modules.sessions.manager import execute_query as eq
from modules.sessions.manager import execute_script as es
from modules.sessions.manager import execute_updates as eu
from modules.sessions.manager import get_session as gs
from modules.sessions.manager import get_session_driver as gsd
from modules.sessions.manager import has_session as hs
from modules.sessions.manager import is_editable_query as ieq
from modules.sessions.manager import open_session as os
from modules.sessions.manager import test_connection as tc


def open_session(
    connection: Connection,
) -> Session:
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


def close_session(
    connection_id: str,
) -> None:
    """
    Cierra una sesión activa.

    Args:
        connection_id (str):
            Identificador único de la conexión.
    """

    cs(connection_id)


def get_session(
    connection_id: str,
) -> Session | None:
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


def get_session_driver(
    connection_id: str,
) -> Driver | None:
    """
    Recupera una sesión activa registrada.

    Args:
        connection_id (str):
            Identificador único de la conexión.

    Returns:
        Driver | None:
            Driver de la conexión asociada a la sesión
            activa encontrada o None si no existe la sesión.
    """

    return gsd(connection_id)


def has_session(
    connection_id: str,
) -> bool:
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


def test_connection(
    connection: Connection,
) -> bool:
    """
    Verifica conectividad de una sesión activa.

    Args:
        connection (Connection):
            Configuración de conexión que se desea comprobar.

    Returns:
        bool:
            - `True` si la conexión responde correctamente.
    """

    return tc(connection)


def execute_query(
    connection_id: str,
    query: str,
) -> QueryResult:
    """
    Ejecuta una consulta SQL.

    Args:
        connection_id (str):
            Identificador único de la conexión.

        query (str):
            Consulta SQL que debe ejecutarse.

    Returns:
        QueryResult:
            Resultado de la ejecución.
    """

    return eq(connection_id, query)


def is_editable_query(
    query: str,
) -> bool:
    """
    Determina si una consulta admite
    edición gráfica de resultados.

    Args:
        query (str):
            Consulta SQL que se desea evaluar.

    Returns:
        bool:
            - `True` si la consulta es editable.
            - `False` en caso contrario.
    """

    return ieq(query)


def execute_script(
    connection_id: str,
    queries: list[str],
) -> ScriptResult:
    """
    Ejecuta un conjunto de consultas SQL.

    Args:
        connection_id (str):
            Identificador único de la conexión.

        queries (list[str]):
            Consultas SQL que deben ejecutarse.

    Returns:
        ScriptResult:
            Resultado agregado de la ejecución.
    """

    return es(connection_id, queries)


def execute_updates(
    connection_id: str,
    operations: list[UpdateOperation],
) -> ScriptResult:
    """
    Ejecuta una serie de operaciones UPDATE.

    Args:
        connection_id (str):
            Identificador de la conexión sobre la
            que se ejecutarán las operaciones.

        operations (list[UpdateOperation]):
            Operaciones de actualización que se
            desean persistir.

    Returns:
        ScriptResult:
            Resultado de la ejecución.
    """

    return eu(
        connection_id=connection_id,
        operations=operations,
    )


def get_db_tree(
    connection_id: str,
) -> (
    dict[
        str,
        Any,
    ]
    | None
):
    """
    Obtiene la estructura completa de metadatos (tablas y vistas)
    de una base de datos activa.

    Args:
        connection_id:
            Identificador único de la conexión/sesión activa.

    Returns:
        dict[str,Any]:
            Un diccionario con la estructura de la base de datos ("tables" y "views").

        None:
            Si no existe una sesión activa para el identificador proporcionado.
    """

    return gdt(connection_id=connection_id)

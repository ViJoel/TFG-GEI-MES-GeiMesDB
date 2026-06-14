import logging
from typing import Any

from sqlalchemy import inspect, text
from sqlalchemy.engine import CursorResult, Engine
from sqlalchemy.exc import SQLAlchemyError

from entities.connection import Connection
from entities.driver import Driver
from entities.query_result import QueryResult, ResultSet
from entities.script_result_data import ScriptResultData, ScriptResultDataItem
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

# ==================
# === PUBLIC API ===
# ==================


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


def execute_query(
    connection_id: str,
    query: str,
) -> QueryResult:

    session = get_session(connection_id)

    if session is None:
        message = f"There is no active session for the connection {connection_id}."

        logger.warning(message)

        return QueryResult(
            success=False,
            console_output=message,
            result_set=None,
        )

    logger.info(f"Executing SQL on '{session.connection.name}'...")

    try:

        with session.engine.begin() as conn:

            result = conn.execute(text(query))

            logger.success(f"SQL executed successfully on '{session.connection.name}'.")

            if result.returns_rows:

                return _create_query_result(
                    engine=session.engine,
                    query=query,
                    result=result,
                )

            return QueryResult(
                success=True,
                console_output=_create_console_output(
                    query=query,
                    result=result,
                ),
                result_set=None,
            )

    except Exception as e:

        logger.exception(f"Error executing SQL query: {e}")

        return QueryResult(
            success=False,
            console_output=str(e),
            result_set=None,
        )


def is_editable_query(
    query: str,
) -> bool:

    normalized_query = " ".join(query.strip().split()).upper()

    if not normalized_query.startswith("SELECT * FROM "):
        return False

    forbidden_keywords = (
        " JOIN ",
        " WHERE ",
        " GROUP BY ",
        " HAVING ",
        " LIMIT ",
        " DISTINCT ",
        " UNION ",
        " INTERSECT ",
        " EXCEPT ",
        " WITH ",
        " OFFSET ",
        " INTO ",
    )

    for keyword in forbidden_keywords:
        if keyword in normalized_query:
            return False

    return True


def execute_script(
    connection_id: str,
    queries: list[str],
) -> ScriptResultData:

    items = []

    print(queries)
    print(len(queries))

    for query in queries:

        result = execute_query(
            connection_id=connection_id,
            query=query,
        )

        if result.success:

            items.append(
                ScriptResultDataItem(
                    query=query,
                )
            )

        else:

            items.append(
                ScriptResultDataItem(
                    query=query,
                    error=result.console_output,
                )
            )

    return ScriptResultData(
        items=items,
    )


# ===================
# === PRIVATE API ===
# ===================


def _create_query_result(
    engine: Engine,
    query: str,
    result: CursorResult,
) -> QueryResult:

    result_set = _create_result_set(
        engine=engine,
        query=query,
        result=result,
    )

    console_output = (
        _format_result_set(result_set)
        + "\n\n"
        + f"{len(result_set.rows)} row(s) returned."
    )

    return QueryResult(
        success=True,
        console_output=console_output,
        result_set=result_set,
    )


def _create_result_set(
    engine: Engine,
    query: str,
    result: CursorResult,
) -> ResultSet:

    columns = list(result.keys())
    rows = [list(row) for row in result.fetchall()]

    table_name, primary_key_columns = _get_editable_metadata(
        query=query,
        engine=engine,
    )

    return ResultSet(
        rows=rows,
        columns=columns,
        columns_types=_infer_column_types(
            columns=columns,
            rows=rows,
        ),
        table_name=table_name,
        primary_key_columns=primary_key_columns,
    )


def _infer_column_types(
    columns: list[str],
    rows: list[list[Any]],
) -> list[type]:

    columns_types = []

    for i in range(len(columns)):

        column_type = str

        for row in rows:

            value = row[i]

            if value is not None:

                column_type = type(value)
                break

        columns_types.append(column_type)

    return columns_types


def _format_result_set(
    result_set: ResultSet,
) -> str:

    rows = result_set.rows
    columns = result_set.columns

    widths = [len(column) for column in columns]

    for row in rows:

        for i, value in enumerate(row):

            widths[i] = max(
                widths[i],
                len(str(value)),
            )

    header = " | ".join(column.ljust(widths[i]) for i, column in enumerate(columns))

    separator = "-+-".join("-" * width for width in widths)

    body = []

    for row in rows:

        body.append(
            " | ".join(str(value).ljust(widths[i]) for i, value in enumerate(row))
        )

    lines = [
        header,
        separator,
        *body,
    ]

    return "\n".join(lines)


def _create_console_output(
    query: str,
    result: CursorResult,
) -> str:

    command = query.lstrip().split(None, 1)[0].upper()

    if command == "INSERT":
        console_output = f"{result.rowcount} row(s) inserted."

    elif command == "UPDATE":
        console_output = f"{result.rowcount} row(s) updated."

    elif command == "DELETE":
        console_output = f"{result.rowcount} row(s) deleted."

    else:
        console_output = "Query executed successfully."

    return console_output


def _extract_table_name(
    query: str,
) -> str | None:

    normalized_query = " ".join(query.strip().split())

    words = normalized_query.split()

    if len(words) < 4:
        return None

    return words[3].rstrip(";")


def _get_primary_key_columns(
    engine: Engine,
    table_name: str,
) -> list[str]:

    inspector = inspect(engine)

    pk = inspector.get_pk_constraint(table_name)

    return pk.get(
        "constrained_columns",
        [],
    )


def _get_editable_metadata(
    query: str,
    engine: Engine,
) -> tuple[str | None, list[str]]:

    if not is_editable_query(query):
        return None, []

    table_name = _extract_table_name(query)

    if table_name is None:
        return None, []

    primary_key_columns = _get_primary_key_columns(
        engine,
        table_name,
    )

    return table_name, primary_key_columns

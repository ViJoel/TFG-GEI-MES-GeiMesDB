from sqlalchemy import (
    MetaData,
    Table,
    text,
)
from sqlalchemy.engine import (
    CursorResult,
    Engine,
)
from sqlalchemy.exc import SQLAlchemyError

from entities.connection import Connection
from entities.driver import Driver
from entities.query_result import (
    QueryResult,
    ResultSet,
)
from entities.script_result import (
    ScriptResult,
    ScriptResultItem,
)
from entities.session import Session
from entities.table_metadata import TableMetadata
from entities.update_operation import UpdateOperation
from log.app_logger import get_logger

logger = get_logger(__name__)

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


def open_session(
    connection: Connection,
) -> Session:
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

        logger.error(f"Failed to open session for '{connection.name}'.\nException: {e}")

        if session is not None:
            try:
                session.close()
            except Exception:
                pass

        raise


def close_session(
    connection_id: str,
) -> None:
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

    try:

        logger.info(f"Closing session for '{session.connection.name}'...")

        session.close()

        logger.info(
            f"Removing active session registry for '{session.connection.name}'..."
        )

        del _active_sessions[connection_id]

        logger.success(
            f"Active session registry removed for '{session.connection.name}'."
        )

        logger.success(f"Session closed for '{session.connection.name}'.")

    except Exception as e:

        logger.error(
            f"Failed to close session for '{session.connection.name}'.\nException: {e}"
        )

        raise


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

    session = get_session(connection_id)

    if session is None:
        return
    else:
        return session.connection.driver


def has_session(
    connection_id: str,
) -> bool:
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


def test_connection(
    connection: Connection,
) -> bool:
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

        logger.error(f"Connection test failed for '{connection.name}'.\nException: {e}")

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
    """
    Ejecuta una consulta SQL utilizando una
    sesión activa.

    Args:
        connection_id (str):
            Identificador de la conexión cuya
            sesión se utilizará.

        query (str):
            Consulta SQL que debe ejecutarse.

    Returns:
        QueryResult:
            Resultado de la ejecución de la
            consulta.
    """

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

    except SQLAlchemyError as e:

        logger.error(
            f"SQL execution failed.\n"
            f"Connection: '{session.connection.name}'.\n"
            f"Exception: {e}"
        )

        return QueryResult(
            success=False,
            console_output=str(e),
            result_set=None,
        )

    except Exception:

        logger.exception(
            f"Unexpected error executing SQL.\n"
            f"Connection: '{session.connection.name}'."
        )

        return QueryResult(
            success=False,
            console_output="Unexpected internal error.\nSee logs for details.",
            result_set=None,
        )


def is_editable_query(
    query: str,
) -> bool:
    """
    Determina si una consulta permite
    edición gráfica de resultados.

    Solo se consideran editables las
    consultas de la forma:

        SELECT * FROM tabla

    sin cláusulas adicionales.

    Args:
        query (str):
            Consulta SQL a evaluar.

    Returns:
        bool:
            - `True` si la consulta es editable.
            - `False` en caso contrario.
    """

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
) -> ScriptResult:
    """
    Ejecuta secuencialmente varias consultas
    SQL utilizando una sesión activa.

    Args:
        connection_id (str):
            Identificador de la conexión cuya
            sesión se utilizará.

        queries (list[str]):
            Consultas SQL que deben ejecutarse.

    Returns:
        ScriptResult:
            Resultado agregado de las consultas
            ejecutadas.
    """

    items = []

    for query in queries:

        result = execute_query(
            connection_id=connection_id,
            query=query,
        )

        if result.success:

            items.append(
                ScriptResultItem(
                    query=query,
                )
            )

        else:

            items.append(
                ScriptResultItem(
                    query=query,
                    error=result.console_output,
                )
            )

    return ScriptResult(
        items=items,
    )


def execute_updates(
    connection_id: str,
    operations: list[UpdateOperation],
) -> ScriptResult:
    """
    Ejecuta una serie de operaciones UPDATE dentro
    de una única transacción.

    Cada operación se ejecuta utilizando un
    SAVEPOINT para permitir que el resto continúe
    aunque alguna falle. Si al menos una operación
    produce un error, la transacción completa se
    revierte al finalizar.

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

    session = get_session(connection_id)

    if session is None:

        message = f"There is no active session for connection " f"'{connection_id}'."

        logger.warning(message)

        return ScriptResult(
            items=[
                ScriptResultItem(
                    query="",
                    error=message,
                ),
            ],
        )

    logger.info(
        f"Executing {len(operations)} update operation(s) "
        f"on '{session.connection.name}'."
    )

    items: list[ScriptResultItem] = []
    has_errors = False

    with session.engine.connect() as connection:

        transaction = connection.begin()

        try:

            for operation in operations:

                stmt = operation.to_statement()

                sql = operation.to_sql(
                    session.engine.dialect,
                )

                savepoint = connection.begin_nested()

                try:

                    connection.execute(stmt)

                    savepoint.commit()

                    items.append(
                        ScriptResultItem(
                            query=sql,
                        )
                    )

                    logger.success(
                        f"Update executed successfully.\n"
                        f"Connection: '{session.connection.name}'.\n"
                        f"Query: {sql}"
                    )

                except SQLAlchemyError as e:

                    has_errors = True

                    savepoint.rollback()

                    logger.error(
                        f"Failed to execute update.\n"
                        f"Connection: '{session.connection.name}'.\n"
                        f"Query: {sql}\n"
                        f"Exception: {e}"
                    )

                    items.append(
                        ScriptResultItem(
                            query=sql,
                            error=str(e),
                        )
                    )

            if has_errors:

                transaction.rollback()

                logger.warning(
                    f"Transaction rolled back for "
                    f"'{session.connection.name}' because one or more "
                    f"UPDATE operations failed."
                )

            else:

                transaction.commit()

                logger.success(
                    f"Transaction committed successfully for "
                    f"'{session.connection.name}'."
                )

        except Exception:

            transaction.rollback()

            logger.exception(
                f"Unexpected error executing update transaction.\n"
                f"Connection: '{session.connection.name}'."
            )

            raise

    return ScriptResult(
        items=items,
        rolled_back=has_errors,
    )


# ===================
# === PRIVATE API ===
# ===================


def _create_query_result(
    engine: Engine,
    query: str,
    result: CursorResult,
) -> QueryResult:
    """
    Construye un objeto de resultado a partir
    del resultado devuelto por SQLAlchemy.

    Args:
        engine (Engine):
            Motor asociado a la sesión activa.

        query (str):
            Consulta SQL ejecutada.

        result (CursorResult):
            Resultado obtenido tras la ejecución.

    Returns:
        QueryResult:
            Resultado enriquecido con los datos
            tabulares y la salida de consola.
    """

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
    """
    Construye un conjunto de resultados a partir
    del resultado devuelto por SQLAlchemy.
    """

    columns = list(result.keys())
    rows = [list(row) for row in result.fetchall()]

    table_metadata = None

    if is_editable_query(query):

        table_name = _extract_table_name(query)

        if table_name is not None:

            table_metadata = _reflect_table_metadata(
                engine=engine,
                table_name=table_name,
            )

    return ResultSet(
        rows=rows,
        columns=columns,
        table_metadata=table_metadata,
    )


def _reflect_table_metadata(
    engine: Engine,
    table_name: str,
) -> TableMetadata:
    """
    Refleja una tabla existente mediante
    SQLAlchemy.

    Args:
        engine (Engine):
            Motor asociado a la sesión.

        table_name (str):
            Nombre de la tabla.

    Returns:
        TableMetadata:
            Metadatos completos de la tabla.
    """

    metadata = MetaData()

    table = Table(
        table_name,
        metadata,
        autoload_with=engine,
    )

    return TableMetadata(
        table=table,
    )


def _format_result_set(
    result_set: ResultSet,
) -> str:
    """
    Convierte un conjunto de resultados en una
    representación textual tabular.

    Args:
        result_set (ResultSet):
            Resultado que se desea formatear.

    Returns:
        str:
            Representación textual del conjunto
            de resultados.
    """

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
    """
    Genera el mensaje mostrado en consola tras
    ejecutar una consulta que no devuelve filas.

    Args:
        query (str):
            Consulta SQL ejecutada.

        result (CursorResult):
            Resultado devuelto por SQLAlchemy.

    Returns:
        str:
            Mensaje descriptivo del resultado
            obtenido.
    """

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
    """
    Extrae el nombre de la tabla objetivo
    de una consulta editable.

    Args:
        query (str):
            Consulta SQL analizada.

    Returns:
        str | None:
            Nombre de la tabla o `None`
            si no puede determinarse.
    """

    normalized_query = " ".join(query.strip().split())

    words = normalized_query.split()

    if len(words) < 4:
        return None

    return words[3].rstrip(";")

import os
import sqlite3
from collections.abc import Generator
from contextlib import contextmanager

from common.paths import DATA_DIR, DB_PATH, SQL_PATH
from log.app_logger import get_logger

logger = get_logger(__name__)

# True: Evita reinicializar la base de datos si el archivo ya existe.
# False: Fuerza la creación del esquema y la inicialización siempre.
SKIP_INIT_IF_DB_EXISTS = False


@contextmanager
def get_connection(
    db_path: str = DB_PATH,
) -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager para abrir una conexión SQLite.

    Gestiona automáticamente:
        - Apertura de la conexión
        - Commit al finalizar correctamente
        - Rollback en caso de error
        - Cierre de la conexión

    La conexión se abre en modo lectura/escritura (`mode=rw`)
    para evitar la creación automática de bases de datos vacías
    si el archivo no existe.

    Args:
        db_path (str):
            Ruta al archivo de base de datos SQLite.

    Yields:
        sqlite3.Connection:
            Conexión activa a la base de datos.

    Raises:
        sqlite3.Error:
            Propaga cualquier error de SQLite ocurrido durante
            la conexión o transacción.
    """

    logger.debug("Opening SQLite connection.")

    conn = sqlite3.connect(
        f"file:{db_path}?mode=rw",
        uri=True,
    )

    # Permite acceder a las columnas usando nombres
    # en lugar de índices numéricos.
    conn.row_factory = sqlite3.Row

    # SQLite desactiva las foreign keys por conexión,
    # por lo que deben habilitarse manualmente.
    conn.execute("PRAGMA foreign_keys = ON;")

    try:
        yield conn

        # Confirmar transacción únicamente si no hubo errores.
        conn.commit()

    except Exception as e:

        # Revertir todos los cambios pendientes
        # ante cualquier excepción.
        conn.rollback()

        logger.error(f"Transaction failed. Rollback executed.\nException: {e}")

        raise

    finally:

        # Garantiza el cierre de la conexión incluso
        # si ocurre una excepción.
        conn.close()

        logger.debug("SQLite connection closed.")


def init_database(
    db_path: str = DB_PATH,
    sql_path: str = SQL_PATH,
    data_dir: str = DATA_DIR,
) -> None:
    """
    Inicializa la base de datos de la aplicación.

    Responsabilidades:
        - Crear el directorio de datos si no existe.
        - Verificar si la base de datos ya existe.
        - Crear la base de datos si no existe.
        - Aplicar el esquema SQL inicial.

    Comportamiento:
        - Si la base de datos ya existe, la inicialización se omite.
        - Si el archivo SQL no existe, se lanza FileNotFoundError.

    Args:
        db_path (str):
            Ruta del archivo SQLite.

        sql_path (str):
            Ruta del archivo SQL con el esquema inicial.

        data_dir (str):
            Directorio donde se almacenará la base de datos.

    Raises:
        FileNotFoundError:
            Si no se encuentra el archivo de esquema SQL.

        Exception:
            Propaga cualquier error durante la conexión o transacción.
    """

    logger.info("Initializing application database...")

    # Garantiza que el directorio de datos exista
    # antes de crear la base de datos.
    os.makedirs(
        data_dir,
        exist_ok=True,
    )

    if SKIP_INIT_IF_DB_EXISTS:
        if os.path.exists(db_path):
            logger.info("Application database already exists. Initialization skipped.")
            return

    try:

        # El esquema SQL debe existir incluso en builds
        # empaquetadas (ej. PyInstaller).
        if not os.path.exists(sql_path):
            raise FileNotFoundError(f"SQL file not found at: {sql_path}")

        # Leer el esquema SQL completo.
        with open(
            sql_path,
            "r",
            encoding="utf-8",
        ) as f:
            schema = f.read()

        # La inicialización utiliza una conexión estándar
        # porque en este punto la base de datos aún no existe.
        with sqlite3.connect(db_path) as conn:

            # SQLite requiere activar foreign keys
            # manualmente por sesión.
            conn.execute("PRAGMA foreign_keys = ON;")

            logger.info("Creating database schema...")

            conn.executescript(schema)

            conn.commit()

        logger.success("Application database initialized successfully.")

    except Exception as e:
        logger.critical(f"Database initialization failed.\nException: {e}")
        raise

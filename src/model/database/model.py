import logging
import os
import sqlite3
from contextlib import contextmanager

from common.paths import DATA_DIR, DB_PATH, SQL_PATH

logger = logging.getLogger(__name__)


@contextmanager
def get_connection():
    """
    Abre una conexión SQLite gestionando automáticamente
    commit, rollback y cierre de recursos.

    La conexión se abre en modo lectura/escritura (`mode=rw`)
    para evitar que SQLite cree automáticamente una base
    de datos vacía si el archivo no existe.

    Yields:
        sqlite3.Connection:
            Conexión activa a la base de datos.

    Raises:
        sqlite3.Error:
            Si ocurre un error durante la conexión
            o la transacción.
    """

    conn = sqlite3.connect(
        f"file:{DB_PATH}?mode=rw",
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

        logger.error(f"Error en transacción: {e}")

        raise

    finally:

        # Garantiza el cierre de la conexión incluso
        # si ocurre una excepción.
        conn.close()


def init_database() -> None:
    """
    Inicializa la base de datos de la aplicación.

    Responsabilidades:
        - Crear el directorio de datos si no existe.
        - Crear la base de datos inicial.
        - Aplicar el esquema SQL base.
        - Evitar reinicializaciones accidentales.

    Raises:
        FileNotFoundError:
            Si el archivo de esquema SQL no existe.

        sqlite3.Error:
            Si ocurre un error durante la creación
            o inicialización de la base de datos.
    """

    # Garantiza que el directorio de datos exista
    # antes de crear la base de datos.
    os.makedirs(DATA_DIR, exist_ok=True)

    # Evita sobrescribir una base de datos ya inicializada.
    if os.path.exists(DB_PATH):
        logger.info("La base de datos ya existe. Omitiendo inicialización.")
        return

    try:

        # El esquema SQL debe existir incluso en builds
        # empaquetadas (ej. PyInstaller).
        if not os.path.exists(SQL_PATH):
            raise FileNotFoundError(f"SQL file not found at: {SQL_PATH}")

        # Leer el esquema SQL completo.
        with open(SQL_PATH, "r", encoding="utf-8") as f:
            schema = f.read()

        # La inicialización utiliza una conexión estándar
        # porque en este punto la base de datos aún no existe.
        with sqlite3.connect(DB_PATH) as conn:

            # SQLite requiere activar foreign keys
            # manualmente por sesión.
            conn.execute("PRAGMA foreign_keys = ON;")

            # Ejecutar todas las sentencias SQL del esquema.
            conn.executescript(schema)

            conn.commit()

        logger.info("Base de datos creada e inicializada por primera vez.")

    except Exception as e:
        logger.error(f"Fallo crítico al crear la BD: {e}")
        raise

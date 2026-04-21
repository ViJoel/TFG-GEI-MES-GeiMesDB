import logging
import os
import sqlite3
import sys
from contextlib import contextmanager
from common.paths import DB_PATH, DATA_DIR, SQL_PATH

# Esto crea un sub-logger llamado 'model.connections.database'
logger = logging.getLogger(__name__)

@contextmanager
def get_connection():
    """
    Establece una conexión, gestiona transacciones y asegura el cierre.
    Si algo falla dentro del bloque 'with', hace rollback explícito.
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    except Exception as e:
        conn.rollback()  # Rollback explícito ante cualquier error
        logger.error(f"Error en transacción: {e}")
        raise
    finally:
        conn.close()


def init_database():
    """
    Inicializa la base de datos solo si no existe el archivo .db.
    """

    # Asegurar directorio de datos
    # exist_ok=True evita que falle si ya existe el directorio
    os.makedirs(DATA_DIR, exist_ok=True)

    # Si el archivo .db ya existe, no hacemos nada y salimos de la función
    if os.path.exists(DB_PATH):
        logger.info("La base de datos ya existe. Omitiendo inicialización.")
        return

    # Si el archivo .db no existe, procedemos a crearla con el esquema
    try:
        # Validar la existencia del archivo de esquema (.sql) antes de intentar leerlo
        # Es vital para detectar errores de empaquetado con PyInstaller
        if not os.path.exists(SQL_PATH):
            raise FileNotFoundError(f"SQL file not found at: {SQL_PATH}")

        # Leer el contenido del script SQL con codificación UTF-8
        with open(SQL_PATH, "r", encoding="utf-8") as f:
            schema = f.read()

        # Establecer conexión y aplicar los cambios
        with get_connection() as conn:
            # Forzar la activación de claves foráneas en SQLite (se desactivan por sesión)
            conn.execute("PRAGMA foreign_keys = ON;")
            # Ejecutar todas las sentencias del archivo .sql
            conn.executescript(schema)
            conn.commit()

        logger.info("Base de datos creada e inicializada por primera vez.")
    except Exception as e:
        logger.error(f"Fallo crítico al crear la BD: {e}")
        raise

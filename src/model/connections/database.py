import logging
import os
import sqlite3
import sys

# Esto crea un sub-logger llamado 'model.connections.database'
logger = logging.getLogger(__name__)

# Ruta para RECURSOS (Archivos que vienen dentro del ejecutable)
if getattr(sys, "frozen", False):
    # En el ejecutable, PyInstaller descomprime los recursos en esta carpeta temporal
    RESOURCE_PATH = sys._MEIPASS
else:
    # En desarrollo, subimos un nivel desde model/connections/ hacia la raíz del proyecto src/
    RESOURCE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Ruta para DATOS (Archivos que el usuario genera y deben persistir)
if getattr(sys, "frozen", False):
    # Al lado del ejecutable real
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # En desarrollo, usamos la raíz del proyecto
    BASE_DIR = RESOURCE_PATH

# Definición de rutas finales
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "connections.db")
# El SQL se busca siempre en la carpeta de recursos (dentro del ejecutable o raíz del proyecto)
SQL_PATH = os.path.join(RESOURCE_PATH, "sql", "connections.sql")


def get_connection():
    """
    Establece y devuelve una conexión a la base de datos SQLite.

    Esta función utiliza la ruta absoluta definida en DB_PATH para conectar
    con el archivo de base de datos que almacena la configuración de las conexiones.

    Returns:
        sqlite3.Connection: Un objeto de conexión activo hacia la base de datos.
    """
    return sqlite3.connect(DB_PATH)


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

        logger.info("Base de datos creada e inicializada por primera vez.")
    except Exception as e:
        logger.error(f"Fallo crítico al crear la BD: {e}")
        raise

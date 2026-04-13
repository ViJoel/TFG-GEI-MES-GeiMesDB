import os
import sqlite3
import sys

# Directorio base de la app
if getattr(sys, "frozen", False):
    # Ejecutable compilado -> /ruta/al/ejecutable
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Modo desarrollo -> /ruta/proyecto/src/model
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Rutas principales
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "connections.db")
SQL_PATH = os.path.join(BASE_DIR, "sql", "connections.sql")


def get_connection():
    """Devuelve una conexión a la base de datos."""

    return sqlite3.connect(DB_PATH)


def init_database():
    """Inicializa la base de datos si no existe."""

    # Crea la carpeta data/
    os.makedirs(DATA_DIR, exist_ok=True)

    # Comprueba que existe el schema SQL
    if not os.path.exists(SQL_PATH):
        raise FileNotFoundError(f"SQL file not found: {SQL_PATH}")

    # Lee el archivo SQL
    with open(SQL_PATH, "r", encoding="utf-8") as f:
        schema = f.read()

    # Ejecuta el schema en la base de datos
    with get_connection() as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.executescript(schema)

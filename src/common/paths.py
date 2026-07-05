import os
import sys

from .constants import (
    DATA_DIR_NAME,
    DB_FILE_NAME,
    DB_SQL_DDL_FILE,
    LOG_DIR_NAME,
    LOG_FILE_NAME,
)

if getattr(sys, "frozen", False):
    # Producción
    RESOURCE_ROOT = sys._MEIPASS  # Carpeta temporal de PyInstaller
    BASE_DIR = os.path.dirname(sys.executable)  # Carpeta del ejecutable
else:
    # Desarrollo
    RESOURCE_ROOT = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )  # Raíz del proyecto
    BASE_DIR = RESOURCE_ROOT

# Ruta a los archivos sql
SQL_DIR = os.path.join(RESOURCE_ROOT, "data")
SQL_PATH = os.path.join(SQL_DIR, DB_SQL_DDL_FILE)

# Directorio de datos y archivo de base de datos
DATA_DIR = os.path.join(BASE_DIR, DATA_DIR_NAME)
DB_PATH = os.path.join(DATA_DIR, DB_FILE_NAME)

# Logs
LOG_DIR = os.path.join(BASE_DIR, LOG_DIR_NAME)
LOG_FILE = os.path.join(LOG_DIR, LOG_FILE_NAME)

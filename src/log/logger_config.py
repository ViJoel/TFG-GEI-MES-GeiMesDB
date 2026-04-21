import os
import sys
import logging


def setup_logging():
    """Configura el sistema de logging de la aplicación.

    Define las rutas para los archivos de log tanto en entorno de desarrollo
    como en el ejecutable final, asegurando que los directorios existan.
    """

    # Determinar el directorio base
    if getattr(sys, "frozen", False):
        base_dir = os.path.dirname(sys.executable)
    else:
        # Subimos un nivel para llegar a la raíz
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Configurar la carpeta de logs
    log_dir = os.path.join(base_dir, "geimesdb_logs")
    os.makedirs(log_dir, exist_ok=True)

    # Configurar archivo de logs
    log_file = os.path.join(log_dir, "app.log")

    # Configuración global
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            # 'encoding="utf-8"' es vital para evitar errores en Windows con acentos
            logging.FileHandler(
                log_file, encoding="utf-8", mode="w"
            ),  # 'w' sobreescribe el archivo (solo para desarrollo, quitar el argumento para producción)
            # El StreamHandler mantiene la salida por consola para desarrollo
            logging.StreamHandler(sys.stdout),
        ],
    )

    logger = logging.getLogger(__name__)
    logger.info(f"Sistema de logs iniciado. Archivo: {log_file}")

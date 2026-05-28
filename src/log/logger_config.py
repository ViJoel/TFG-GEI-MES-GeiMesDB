import logging
import os
import sys


def setup_logging():
    """
    Configura el sistema global de logging de la aplicación.

    Responsabilidades:
        - Resolver rutas según entorno de ejecución.
        - Crear el directorio de logs si no existe.
        - Configurar salida a archivo y consola.
        - Definir el formato global de logs.

    La configuración soporta tanto:
        - ejecución en desarrollo
        - ejecutables empaquetados (PyInstaller)
    """

    # En aplicaciones empaquetadas, el ejecutable es
    # la referencia correcta para resolver rutas.
    if getattr(sys, "frozen", False):
        base_dir = os.path.dirname(sys.executable)

    # En desarrollo se toma la raíz del proyecto.
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Directorio donde se almacenarán los logs.
    log_dir = os.path.join(base_dir, "geimesdb_logs")
    os.makedirs(log_dir, exist_ok=True)

    # Archivo principal de logs.
    log_file = os.path.join(log_dir, "app.log")

    # Configuración global
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            # UTF-8 evita problemas de codificación especialmente en Windows.
            logging.FileHandler(
                log_file, encoding="utf-8", mode="w"
            ),  # mode="w" sobreescribe el archivo (solo para desarrollo, quitar el argumento para producción)
            # Mantiene salida visible por consola durante desarrollo.
            logging.StreamHandler(sys.stdout),
        ],
    )

    logger = logging.getLogger(__name__)

    logger.info(f"Sistema de logs iniciado. Archivo: {log_file}")

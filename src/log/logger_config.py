import logging
import os
import sys

from colorlog import ColoredFormatter

# Nivel personalizado para operaciones
# completadas correctamente.
SUCCESS = 25

logging.addLevelName(SUCCESS, "SUCCESS")


def success(self, message, *args, **kwargs):
    """
    Añade soporte para logger.success().
    """

    if self.isEnabledFor(SUCCESS):
        self._log(SUCCESS, message, args, **kwargs)


logging.Logger.success = success


def setup_logging():
    """
    Configura el sistema global de logging de la aplicación.

    Responsabilidades:
        - Resolver rutas según entorno de ejecución.
        - Crear el directorio de logs si no existe.
        - Configurar salida a archivo y consola.
        - Definir el formato global de logs.

    La configuración soporta tanto:
        - Ejecución en desarrollo
        - Ejecutables empaquetados (PyInstaller)
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

    # ====================
    # === FILE HANDLER ===
    # ====================

    file_handler = logging.FileHandler(
        log_file,
        encoding="utf-8",
        mode="w",
    )

    file_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)-8s] %(name)s: %(message)s")
    )

    # =======================
    # === CONSOLE HANDLER ===
    # =======================

    console_handler = logging.StreamHandler(sys.stdout)

    console_handler.setFormatter(
        ColoredFormatter(
            "%(log_color)s%(asctime)s " "[%(levelname)s] " "%(name)s: " "%(message)s",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "white",
                "SUCCESS": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
        )
    )

    # =====================
    # === GLOBAL CONFIG ===
    # =====================

    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[
            file_handler,
            console_handler,
        ],
    )

    logger = logging.getLogger(__name__)

    logger.info(f"Sistema de logs iniciado. Archivo: {log_file}")

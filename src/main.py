"""
Punto de entrada principal de la aplicación.

Responsabilidades:
- Inicializar logging.
- Inicializar la base de datos local.
- Crear la aplicación Qt.
- Construir la ventana principal.
- Gestionar el ciclo de vida global.
"""

import sys

from PySide6 import QtWidgets

from log.logger_config import setup_logging
from modules.database.model import init_database
from modules.sessions.service import close_all_sessions
from ui.app.main_window import MainWindow
from ui.themes.theme_manager import ThemeManager


def shutdown() -> None:
    """
    Ejecuta el proceso global de apagado
    de la aplicación.

    Responsabilidades:
    - Liberar sesiones activas.
    - Cerrar conexiones abiertas.
    - Ejecutar cleanup global.
    """

    close_all_sessions()


def main() -> int:
    """
    Inicializa y ejecuta la aplicación Qt.

    Returns:
        int:
            Código de salida del proceso.
    """

    # Inicializar sistema de logs.
    setup_logging()

    # Inicializar base de datos interna.
    init_database()

    # Crear aplicación Qt.
    app = QtWidgets.QApplication(sys.argv)

    # Inicializar tema.
    ThemeManager.initialize(app)

    # Registrar cleanup global.
    app.aboutToQuit.connect(shutdown)

    # Crear ventana principal.
    window = MainWindow()

    # Mostrar maximizada.
    window.showMaximized()

    # Ejecutar event loop Qt.
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

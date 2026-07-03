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

from log.app_logger import setup_logging
from modules.database.model import init_database
from modules.sessions.service import close_all_sessions
from ui.app.app_context import AppContext
from ui.app.main_window import MainWindow
from ui.themes.theme_manager import ThemeManager
from ui.widgets.notifications.notification_manager import NotificationManager


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

    # Inicializar contexto de la aplicación.
    AppContext.initialize(app)

    # Inicializar tema.
    ThemeManager.initialize()

    # Registrar cleanup global.
    app.aboutToQuit.connect(shutdown)

    # Crear ventana principal.
    window = MainWindow()

    # Crear manejador de notificaciones.
    AppContext.set_notification_manager(NotificationManager())
    AppContext.get_notification_manager().set_main_window(window)

    # Mostrar maximizada.
    window.showMaximized()

    # Ejecutar event loop Qt.
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

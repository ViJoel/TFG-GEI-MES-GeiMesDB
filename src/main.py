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

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from log.app_logger import setup_logging
from modules.database.model import init_database
from modules.sessions.service import close_all_sessions
from ui.app.app_context import AppContext
from ui.app.main_window import MainWindow
from ui.app.task_manager import TaskManager
from ui.themes.theme_manager import ThemeManager
from ui.translations.translation_manager import TranslationManager
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

    # Configurar política de escalado High-DPI
    # (debe ir ANTES de instanciar QApplication).
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    # Crear aplicación Qt.
    app = QApplication(sys.argv)

    # Inicializar contexto de la aplicación.
    AppContext.initialize(app)

    # Registrar TaskManager global.
    AppContext.set_task_manager(TaskManager())

    # Inicializar tema.
    ThemeManager.initialize()

    # Inicializar lenguaje.
    TranslationManager.initialize()

    # Registrar cleanup global.
    app.aboutToQuit.connect(shutdown)

    # Crear ventana principal.
    window = MainWindow()

    # Crear manejador de notificaciones.
    notification_manager = NotificationManager()
    notification_manager.set_main_window(window)

    AppContext.set_notification_manager(notification_manager)

    # Mostrar maximizada.
    window.showMaximized()

    # Ejecutar event loop Qt.
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

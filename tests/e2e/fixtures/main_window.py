from collections.abc import Generator

import pytest
from pytestqt.qtbot import QtBot
from qtpy.QtWidgets import QApplication

from main import shutdown
from ui.app.app_context import AppContext
from ui.app.main_window import MainWindow
from ui.app.task_manager import TaskManager
from ui.themes.theme_manager import ThemeManager
from ui.translations.translation_manager import TranslationManager
from ui.widgets.notifications.notification_manager import NotificationManager


@pytest.fixture
def main_window(
    qtbot: QtBot,
    temporary_database,
    temporary_logging,
) -> Generator[MainWindow, None, None]:
    """
    Construye la ventana principal de la aplicación
    sobre una base de datos temporal.

    Yields:
        MainWindow:
            Ventana principal lista para ser utilizada
            por los tests E2E.
    """

    app = QApplication.instance()

    assert app is not None

    AppContext.initialize(app)

    AppContext.set_task_manager(
        TaskManager(),
    )

    ThemeManager.initialize()

    TranslationManager.initialize()

    window = MainWindow()

    notification_manager = NotificationManager()
    notification_manager.set_main_window(window)

    AppContext.set_notification_manager(
        notification_manager,
    )

    qtbot.addWidget(window)

    window.show()

    yield window

    shutdown()

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QApplication

from ui.app.task_manager import TaskManager

if TYPE_CHECKING:
    from ui.widgets.notifications.notification_manager import NotificationManager


class AppContext:
    """
    Contenedor global de servicios de la aplicación.

    Centraliza el acceso a recursos compartidos que deben
    estar disponibles desde cualquier parte de la aplicación,
    como la instancia de QApplication y servicios globales.
    """

    app: QApplication | None = None
    notification_manager: NotificationManager | None = None
    task_manager: TaskManager | None = None

    @classmethod
    def initialize(cls, app: QApplication):
        """
        Inicializa el contexto global de la aplicación.

        Registra la instancia de QApplication para que
        pueda ser utilizada por otros componentes
        mediante AppContext.

        Args:
            app (QApplication):
                Instancia principal de la aplicación Qt.
        """

        cls.app = app

    @classmethod
    def get_app(cls) -> QApplication:
        """
        Obtiene la instancia global de QApplication.

        Returns:
            QApplication:
                Instancia registrada de la aplicación Qt.

        Raises:
            RuntimeError:
                Si AppContext no ha sido inicializado.
        """

        if cls.app is None:
            raise RuntimeError("AppContext has not been initialized.")

        return cls.app

    @classmethod
    def set_notification_manager(
        cls,
        notification_manager: NotificationManager,
    ) -> None:
        """
        Registra el gestor global de notificaciones.

        Args:
            notification_manager (NotificationManager):
                Instancia del gestor de notificaciones.
        """

        cls.notification_manager = notification_manager

    @classmethod
    def get_notification_manager(
        cls,
    ) -> NotificationManager:
        """
        Obtiene el gestor global de notificaciones.

        Returns:
            NotificationManager:
                Instancia registrada del gestor de notificaciones.

        Raises:
            RuntimeError:
                Si el gestor de notificaciones no ha sido registrado.
        """

        if cls.notification_manager is None:
            raise RuntimeError("NotificationManager has not been initialized.")

        return cls.notification_manager

    @classmethod
    def set_task_manager(
        cls,
        task_manager: TaskManager,
    ):

        cls.task_manager = task_manager

    @classmethod
    def get_task_manager(cls) -> TaskManager:

        if cls.task_manager is None:
            raise RuntimeError("TaskManager has not been initialized.")

        return cls.task_manager

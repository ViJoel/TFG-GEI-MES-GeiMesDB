from ui.widgets.notifications.notification_manager import NotificationManager


class AppContext:
    """
    Contenedor global de servicios de la aplicación.
    """

    notification_manager = NotificationManager()

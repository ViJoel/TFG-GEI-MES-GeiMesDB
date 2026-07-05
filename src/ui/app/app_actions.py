from entities.message_type import MessageType
from log.app_logger import get_logger
from ui.app.app_context import AppContext
from ui.widgets.notifications.notification import Notification

logger = get_logger(__name__)


def notify(
    message_type: MessageType,
    message: str,
) -> None:
    """
    Muestra una notificación al usuario.

    Args:
        message_type (MessageType):
            Tipo de mensaje asociado a la
            notificación.

        message (str):
            Texto que se mostrará en la
            notificación.
    """

    logger.debug("Showing notification...")

    AppContext.notification_manager.show_notification(
        Notification(
            message_type,
            message,
        )
    )

    logger.debug("Notification showed.")

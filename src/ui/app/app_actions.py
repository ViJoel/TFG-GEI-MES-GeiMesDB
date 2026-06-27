import logging

from ui.app.app_context import AppContext
from ui.widgets.notifications.notification import Notification
from ui.widgets.notifications.notification_type import NotificationType

logger = logging.getLogger(__name__)


def notify(
    notification_type: NotificationType,
    message: str,
) -> None:

    logger.debug("Showing notification...")

    AppContext.notification_manager.show_notification(
        Notification(
            notification_type,
            message,
        )
    )

    logger.debug("Notification showed.")

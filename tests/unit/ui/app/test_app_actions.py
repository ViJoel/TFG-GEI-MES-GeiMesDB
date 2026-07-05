from unittest.mock import MagicMock

import ui.app.app_actions as app_actions
from entities.message_type import MessageType


def test_notify_creates_notification(monkeypatch):
    """
    Verifica que notify crea una Notification con
    los parámetros recibidos.
    """

    notification = MagicMock()

    notification_cls = MagicMock(return_value=notification)

    monkeypatch.setattr(
        app_actions,
        "Notification",
        notification_cls,
    )

    manager = MagicMock()

    monkeypatch.setattr(
        app_actions.AppContext,
        "notification_manager",
        manager,
    )

    app_actions.notify(
        MessageType.SUCCESS,
        "Done",
    )

    notification_cls.assert_called_once_with(
        MessageType.SUCCESS,
        "Done",
    )


def test_notify_shows_notification(monkeypatch):
    """
    Verifica que notify delega la visualización en
    el NotificationManager.
    """

    notification = MagicMock()

    monkeypatch.setattr(
        app_actions,
        "Notification",
        MagicMock(return_value=notification),
    )

    manager = MagicMock()

    monkeypatch.setattr(
        app_actions.AppContext,
        "notification_manager",
        manager,
    )

    app_actions.notify(
        MessageType.ERROR,
        "Error",
    )

    manager.show_notification.assert_called_once_with(notification)

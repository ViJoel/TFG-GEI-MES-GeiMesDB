from unittest.mock import MagicMock

import pytest
from PySide6.QtCore import QPoint
from PySide6.QtWidgets import QMainWindow

from entities.message_type import MessageType
from ui.widgets.notifications.notification import Notification
from ui.widgets.notifications.notification_manager import NotificationManager

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def manager():
    """
    Crea un gestor de notificaciones.
    """

    return NotificationManager()


@pytest.fixture
def main_window(qtbot):
    """
    Crea una ventana principal.
    """

    window = QMainWindow()
    window.resize(800, 600)

    qtbot.addWidget(window)
    window.show()

    return window


@pytest.fixture
def notification(qtbot):
    """
    Crea una notificación.
    """

    notification = Notification(
        MessageType.SUCCESS,
        "Test",
    )

    qtbot.addWidget(notification)

    return notification


# =============================================================================
# INITIALIZATION
# =============================================================================


def test_manager_is_created(manager):
    """
    Verifica que el gestor se crea correctamente.
    """

    assert manager.main_window is None
    assert manager.notifications == []
    assert manager.margin == 16
    assert manager.spacing == 10


# =============================================================================
# MAIN WINDOW
# =============================================================================


def test_set_main_window_registers_window(manager, main_window):
    """
    Verifica que el gestor registra la ventana principal.
    """

    manager.set_main_window(main_window)

    assert manager.main_window is main_window


# =============================================================================
# SHOW NOTIFICATION
# =============================================================================


def test_show_notification_adds_notification(
    manager,
    main_window,
    notification,
):
    """
    Verifica que una notificación se registra correctamente.
    """

    manager.set_main_window(main_window)

    notification.show = MagicMock()
    notification.start_timer = MagicMock()

    manager.show_notification(notification)

    assert notification in manager.notifications

    notification.show.assert_called_once()
    notification.start_timer.assert_called_once()


def test_show_notification_without_main_window_does_nothing(
    manager,
    notification,
):
    """
    Verifica que no se muestra ninguna notificación sin ventana principal.
    """

    notification.show = MagicMock()
    notification.start_timer = MagicMock()

    manager.show_notification(notification)

    assert manager.notifications == []

    notification.show.assert_not_called()
    notification.start_timer.assert_not_called()


# =============================================================================
# REMOVE
# =============================================================================


def test_remove_removes_notification(
    manager,
    main_window,
    notification,
):
    """
    Verifica que una notificación se elimina correctamente.
    """

    manager.set_main_window(main_window)

    notification.hide = MagicMock()
    notification.deleteLater = MagicMock()

    manager.notifications.append(notification)

    manager._remove(notification)

    assert notification not in manager.notifications

    notification.hide.assert_called_once()
    notification.deleteLater.assert_called_once()


def test_remove_unknown_notification_does_not_fail(
    manager,
    notification,
):
    """
    Verifica que eliminar una notificación desconocida no produce errores.
    """

    notification.hide = MagicMock()
    notification.deleteLater = MagicMock()

    manager._remove(notification)

    notification.hide.assert_called_once()
    notification.deleteLater.assert_called_once()


# =============================================================================
# REPOSITION
# =============================================================================


def test_reposition_without_main_window_does_nothing(manager):
    """
    Verifica que el reposicionamiento no falla sin ventana principal.
    """

    manager._reposition()


def test_reposition_moves_notifications(
    manager,
    main_window,
    notification,
    monkeypatch,
):
    """
    Verifica que las notificaciones se reposicionan.
    """

    manager.set_main_window(main_window)

    manager.notifications.append(notification)

    notification.adjustSize = MagicMock()
    notification.move = MagicMock()
    notification.width = MagicMock(return_value=100)
    notification.height = MagicMock(return_value=40)

    monkeypatch.setattr(
        main_window,
        "mapToGlobal",
        MagicMock(return_value=QPoint(0, 0)),
    )

    manager._reposition()

    notification.adjustSize.assert_called_once()
    notification.move.assert_called_once()


# =============================================================================
# PUBLIC API
# =============================================================================


def test_reposition_calls_private_method(
    manager,
    monkeypatch,
):
    """
    Verifica que reposition delega en el método privado.
    """

    reposition = MagicMock()

    monkeypatch.setattr(
        manager,
        "_reposition",
        reposition,
    )

    manager.reposition()

    reposition.assert_called_once()


def test_close_signal_removes_notification(
    manager,
    main_window,
    notification,
):
    """
    Verifica que cerrar una notificación la elimina del gestor.
    """

    manager.set_main_window(main_window)

    notification.start_timer = MagicMock()

    manager.show_notification(notification)

    assert notification in manager.notifications

    notification.close_requested.emit()

    assert notification not in manager.notifications


# =============================================================================
# CLEAR
# =============================================================================


def test_clear_removes_all_notifications(
    manager,
    notification,
):
    """
    Verifica que se eliminan todas las notificaciones registradas.
    """

    notification_2 = MagicMock()
    notification_3 = MagicMock()

    manager.notifications.extend(
        [
            notification,
            notification_2,
            notification_3,
        ],
    )

    remove = MagicMock()

    manager._remove = remove

    manager.clear()

    assert remove.call_count == 3

    remove.assert_any_call(notification)
    remove.assert_any_call(notification_2)
    remove.assert_any_call(notification_3)

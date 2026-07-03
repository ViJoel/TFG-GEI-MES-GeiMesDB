import pytest

from entities.message_type import MessageType
from ui.widgets.notifications.notification import Notification

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def notification(qtbot):
    """
    Crea una notificación de prueba.
    """

    notification = Notification(
        MessageType.SUCCESS,
        "Operación completada.",
    )

    qtbot.addWidget(notification)
    notification.show()

    return notification


# =============================================================================
# INITIALIZATION
# =============================================================================


def test_notification_is_created(notification):
    """
    Verifica que la notificación se crea correctamente.
    """

    assert notification.objectName() == "notification"
    assert notification.isVisible()


def test_notification_stores_constructor_arguments(notification):
    """
    Verifica que la notificación almacena los argumentos del constructor.
    """

    assert notification.message_type == MessageType.SUCCESS
    assert notification.message == "Operación completada."
    assert notification.duration_ms is None


def test_notification_sets_type_property(notification):
    """
    Verifica que la propiedad type coincide con el tipo de notificación.
    """

    assert notification.property("type") == MessageType.SUCCESS.value


# =============================================================================
# UI HELPERS
# =============================================================================


@pytest.mark.parametrize(
    ("message_type", "expected_icon"),
    [
        (MessageType.SUCCESS, "fa5s.check-circle"),
        (MessageType.ERROR, "fa5s.times-circle"),
        (MessageType.INFO, "fa5s.info-circle"),
        (MessageType.WARNING, "fa5s.exclamation-triangle"),
    ],
)
def test_get_icon_name_returns_expected_icon(message_type, expected_icon):
    """
    Verifica que cada tipo devuelve el icono correspondiente.
    """

    notification = Notification(
        message_type,
        "Test",
    )

    assert notification._get_icon_name() == expected_icon


def test_get_icon_color_returns_a_color(notification):
    """
    Verifica que el color del icono se obtiene correctamente.
    """

    color = notification._get_icon_color()

    assert isinstance(color, str)
    assert color


# =============================================================================
# PRIVATE API
# =============================================================================


def test_get_duration_returns_default_value(notification):
    """
    Verifica que la duración por defecto es de 3000 ms.
    """

    assert notification._get_duration() == 3000


def test_get_duration_returns_custom_value(qtbot):
    """
    Verifica que la duración personalizada tiene prioridad.
    """

    notification = Notification(
        MessageType.SUCCESS,
        "Test",
        duration_ms=5000,
    )

    qtbot.addWidget(notification)

    assert notification._get_duration() == 5000


# =============================================================================
# SIGNALS
# =============================================================================


def test_close_button_emits_close_requested(notification, qtbot):
    """
    Verifica que el botón de cierre emite la señal correspondiente.
    """

    with qtbot.waitSignal(notification.close_requested):
        notification.close_button.click()


def test_request_close_emits_close_requested(notification, qtbot):
    """
    Verifica que solicitar el cierre emite la señal correspondiente.
    """

    with qtbot.waitSignal(notification.close_requested):
        notification._request_close()


# =============================================================================
# PUBLIC API
# =============================================================================


def test_start_timer_starts_single_shot_timer(monkeypatch, notification):
    """
    Verifica que start_timer inicia el temporizador automático.
    """

    called = {}

    def fake_single_shot(duration, callback):
        called["duration"] = duration
        called["callback"] = callback

    monkeypatch.setattr(
        "ui.widgets.notifications.notification.QTimer.singleShot",
        fake_single_shot,
    )

    notification.start_timer()

    assert called["duration"] == 3000
    assert called["callback"] == notification._request_close


@pytest.mark.parametrize(
    "message_type",
    list(MessageType),
)
def test_notification_sets_type_property_for_every_message_type(message_type):
    """
    Verifica que la propiedad type coincide con el tipo de mensaje.
    """

    allowed_types = [
        MessageType.ERROR,
        MessageType.INFO,
        MessageType.SUCCESS,
        MessageType.WARNING,
    ]

    if message_type not in allowed_types:
        return

    notification = Notification(
        message_type,
        "Test",
    )

    assert notification.property("type") == message_type.value

from unittest.mock import MagicMock

import pytest
from PySide6.QtCore import (
    QPointF,
    Qt,
)
from PySide6.QtGui import (
    QIcon,
    QMouseEvent,
)
from PySide6.QtTest import QTest

import ui.widgets.sidebar.icon_button as icon_button_module
from ui.widgets.sidebar.icon_button import IconButton

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def button(qtbot):
    """
    Construye un IconButton de prueba.
    """

    widget = IconButton(
        "fa5s.plus",
        "primary",
    )

    qtbot.addWidget(widget)

    return widget


# =============================================================================
# INITIALIZATION
# =============================================================================


def test_button_is_created(button):
    """
    Verifica que el botón se crea correctamente.
    """

    assert button.objectName() == "primary"
    assert button._icon_name == "fa5s.plus"
    assert button._hover is False
    assert button._pressed is False


# =============================================================================
# UI HELPERS
# =============================================================================


def test_prefix_returns_expected_value(button):
    """
    Verifica que el prefijo se construye correctamente.
    """

    assert button._prefix() == "button_primary_color"


def test_get_color_uses_theme_manager(monkeypatch, button):
    """
    Verifica que el color se obtiene desde ThemeManager.
    """

    get_color = MagicMock(return_value="#ffffff")

    monkeypatch.setattr(
        icon_button_module.ThemeManager,
        "get_color",
        get_color,
    )

    color = button._get_color("_hover")

    assert color == "#ffffff"

    get_color.assert_called_once_with(
        "button_primary_color_hover",
    )


def test_make_icon_caches_icons(monkeypatch, button):
    """
    Verifica que los iconos se almacenan en caché.
    """

    icon = MagicMock()

    factory = MagicMock(return_value=icon)

    monkeypatch.setattr(
        icon_button_module.qta,
        "icon",
        factory,
    )

    first = button._make_icon(
        "#ffffff",
        "#000000",
    )

    second = button._make_icon(
        "#ffffff",
        "#000000",
    )

    assert first is second

    factory.assert_called_once()


def test_make_icon_creates_new_icon_for_different_color(
    monkeypatch,
    button,
):
    """
    Verifica que un color diferente genera un nuevo icono.
    """

    factory = MagicMock(
        side_effect=[
            MagicMock(),
            MagicMock(),
        ]
    )

    monkeypatch.setattr(
        icon_button_module.qta,
        "icon",
        factory,
    )

    button._make_icon("#111111", "#000000")
    button._make_icon("#222222", "#000000")

    assert factory.call_count == 2


# =============================================================================
# UI STATE
# =============================================================================


def test_apply_icon_uses_default_color(monkeypatch, button):
    """
    Verifica que el estado normal utiliza el color por defecto.
    """

    make_icon = MagicMock(return_value=QIcon())

    monkeypatch.setattr(
        button,
        "_make_icon",
        make_icon,
    )

    monkeypatch.setattr(
        button,
        "_get_color",
        MagicMock(side_effect=["disabled", "normal"]),
    )

    button._apply_icon()

    make_icon.assert_called_once_with(
        "normal",
        "disabled",
    )


def test_apply_icon_uses_hover_color(monkeypatch, button):
    """
    Verifica que el estado hover utiliza el color correspondiente.
    """

    button._hover = True

    make_icon = MagicMock(return_value=QIcon())

    monkeypatch.setattr(button, "_make_icon", make_icon)
    monkeypatch.setattr(
        button,
        "_get_color",
        MagicMock(side_effect=["disabled", "hover"]),
    )

    button._apply_icon()

    make_icon.assert_called_once_with(
        "hover",
        "disabled",
    )


def test_apply_icon_uses_pressed_color(monkeypatch, button):
    """
    Verifica que el estado pulsado utiliza el color correspondiente.
    """

    button._pressed = True

    make_icon = MagicMock(return_value=QIcon())

    monkeypatch.setattr(button, "_make_icon", make_icon)
    monkeypatch.setattr(
        button,
        "_get_color",
        MagicMock(side_effect=["disabled", "pressed"]),
    )

    button._apply_icon()

    make_icon.assert_called_once_with(
        "pressed",
        "disabled",
    )


# =============================================================================
# EVENT HANDLERS
# =============================================================================


def test_enter_event_sets_hover(button):
    """
    Verifica que enterEvent activa el estado hover.
    """

    button._apply_icon = MagicMock()

    button._hover = False

    button.enterEvent(None)

    assert button._hover is True
    button._apply_icon.assert_called_once()


def test_leave_event_clears_hover(button):
    """
    Verifica que leaveEvent desactiva el estado hover.
    """

    button._apply_icon = MagicMock()

    button._hover = True

    button.leaveEvent(None)

    assert button._hover is False
    button._apply_icon.assert_called_once()


def test_mouse_press_sets_pressed(button):
    """
    Verifica que mousePressEvent activa el estado pulsado.
    """

    button.show()

    QTest.mousePress(
        button,
        Qt.MouseButton.LeftButton,
    )

    assert button._pressed is True


def test_mouse_release_clears_pressed(button):
    """
    Verifica que mouseReleaseEvent desactiva el estado pulsado.
    """

    button.show()

    QTest.mousePress(
        button,
        Qt.MouseButton.LeftButton,
    )

    assert button._pressed is True

    QTest.mouseRelease(
        button,
        Qt.MouseButton.LeftButton,
    )

    assert button._pressed is False


def test_set_enabled_reapplies_icon(monkeypatch, button):
    """
    Verifica que cambiar el estado del botón reaplica el icono.
    """

    apply_icon = MagicMock()

    monkeypatch.setattr(
        button,
        "_apply_icon",
        apply_icon,
    )

    button.setEnabled(False)

    apply_icon.assert_called_once()


def test_mouse_move_outside_clears_pressed(button):
    """
    Verifica que mover el ratón fuera del botón desactiva el estado pulsado.
    """

    button._pressed = True
    button._apply_icon = MagicMock()

    event = QMouseEvent(
        QMouseEvent.Type.MouseMove,
        QPointF(-1, -1),
        Qt.MouseButton.NoButton,
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier,
    )

    button.mouseMoveEvent(event)

    assert button._pressed is False
    button._apply_icon.assert_called_once()


def test_mouse_move_inside_keeps_pressed(button):
    """
    Verifica que mover el ratón dentro del botón no modifica el estado pulsado.
    """

    button._pressed = True
    button._apply_icon = MagicMock()

    event = QMouseEvent(
        QMouseEvent.Type.MouseMove,
        QPointF(5, 5),  # Punto dentro del botón
        Qt.MouseButton.NoButton,
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier,
    )

    button.mouseMoveEvent(event)

    assert button._pressed is True
    button._apply_icon.assert_not_called()

from unittest.mock import MagicMock

import pytest
from PySide6.QtCore import (
    QSize,
    Qt,
)
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QToolButton

import ui.widgets.workspace.sql_editor.toolbar_button as toolbar_button_module
from ui.widgets.workspace.sql_editor.toolbar_button import ToolbarButton

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def button(qtbot):
    """
    Construye un ToolbarButton de prueba.
    """

    widget = ToolbarButton(
        "fa5s.play",
        "execute_query",
        "Execute",
    )

    qtbot.addWidget(widget)

    return widget


# =============================================================================
# INITIALIZATION
# =============================================================================


def test_toolbar_button_is_qtoolbutton(button):
    """
    Verifica que ToolbarButton hereda de QToolButton.
    """

    assert isinstance(button, QToolButton)


def test_toolbar_button_object_name(button):
    """
    Verifica que el objectName se configura correctamente.
    """

    assert button.objectName() == "toolbar_button"


def test_toolbar_button_text(button):
    """
    Verifica que el texto del botón se establece correctamente.
    """

    assert button.text() == "Execute"


def test_toolbar_button_icon_size(button):
    """
    Verifica que el tamaño del icono se configura correctamente.
    """

    assert button.iconSize() == QSize(16, 16)


def test_toolbar_button_style(button):
    """
    Verifica que el botón muestra el texto junto al icono.
    """

    assert button.toolButtonStyle() == Qt.ToolButtonStyle.ToolButtonTextBesideIcon


def test_toolbar_button_has_icon(button):
    """
    Verifica que el botón contiene un icono válido.
    """

    assert not button.icon().isNull()


def test_update_icon_uses_theme_color(monkeypatch, button):
    """
    Verifica que el icono se reconstruye utilizando
    el color obtenido desde ThemeManager.
    """

    get_color = MagicMock(return_value="#123456")
    factory = MagicMock(return_value=QIcon())

    monkeypatch.setattr(
        toolbar_button_module.ThemeManager,
        "get_color",
        get_color,
    )

    monkeypatch.setattr(
        toolbar_button_module.qta,
        "icon",
        factory,
    )

    button._update_icon()

    get_color.assert_called_once_with(
        "toolbar_button_execute_query_icon_color",
    )

    factory.assert_called_once_with(
        "fa5s.play",
        color="#123456",
    )


def test_connect_signals_connects_theme_changed(monkeypatch):
    """
    Verifica que el botón se suscribe al evento
    de cambio de tema.
    """

    connect = MagicMock()

    events = MagicMock()
    events.theme_changed.connect = connect

    monkeypatch.setattr(
        toolbar_button_module.ThemeManager,
        "events",
        MagicMock(return_value=events),
    )

    button = ToolbarButton(
        "fa5s.play",
        "execute_query",
        "Execute",
    )

    connect.assert_called_once_with(
        button._on_theme_changed,
    )


def test_on_theme_changed_updates_icon(button):
    """
    Verifica que un cambio de tema reconstruye
    el icono del botón.
    """

    button._update_icon = MagicMock()

    button._on_theme_changed("dark")

    button._update_icon.assert_called_once()

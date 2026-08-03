import pytest
from PySide6.QtCore import (
    QSize,
    Qt,
)
from PySide6.QtWidgets import QToolButton

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

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QSizePolicy,
    QWidget,
)

from ui.widgets.sidebar.sidebar import Sidebar

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def widget(qtbot, monkeypatch):
    """
    Construye el sidebar aislando sus dependencias.
    """

    monkeypatch.setattr(
        "ui.widgets.sidebar.sidebar.AppLogo",
        lambda: QWidget(),
    )

    monkeypatch.setattr(
        "ui.widgets.sidebar.sidebar.ConnectionsList",
        lambda: QWidget(),
    )

    monkeypatch.setattr(
        "ui.widgets.sidebar.sidebar.SettingsButton",
        lambda: QWidget(),
    )

    sidebar = Sidebar()

    qtbot.addWidget(sidebar)

    return sidebar


# =============================================================================
# INITIALIZATION
# =============================================================================


def test_sidebar_is_created(widget):
    """
    Verifica que el sidebar se crea correctamente.
    """

    assert widget.objectName() == "sidebar"

    assert widget.layout() is widget.main_layout


def test_sidebar_sets_styled_background(widget):
    """
    Verifica que el fondo estilizado está habilitado.
    """

    assert widget.testAttribute(Qt.WidgetAttribute.WA_StyledBackground)


def test_sidebar_creates_connections_list(widget):
    """
    Verifica que el sidebar crea la lista de conexiones.
    """

    assert hasattr(widget, "connections_list")


# =============================================================================
# LAYOUT
# =============================================================================


def test_setup_layout(widget):
    """
    Verifica que el layout principal queda correctamente configurado.
    """

    assert widget.main_layout.contentsMargins().left() == 12
    assert widget.main_layout.contentsMargins().top() == 12
    assert widget.main_layout.contentsMargins().right() == 12
    assert widget.main_layout.contentsMargins().bottom() == 12

    assert widget.main_layout.spacing() == 16

    assert widget.sizePolicy().horizontalPolicy() == QSizePolicy.Policy.Fixed
    assert widget.sizePolicy().verticalPolicy() == QSizePolicy.Policy.Expanding

    assert widget.width() == 240

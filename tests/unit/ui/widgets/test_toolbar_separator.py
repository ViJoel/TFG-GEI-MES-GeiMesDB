import pytest
from PySide6.QtWidgets import QFrame

from ui.widgets.workspace.sql_editor.toolbar_separator import ToolbarSeparator

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def separator(qtbot):
    """
    Construye un ToolbarSeparator de prueba.
    """

    widget = ToolbarSeparator()

    qtbot.addWidget(widget)

    return widget


# =============================================================================
# INITIALIZATION
# =============================================================================


def test_toolbar_separator_is_qframe(separator):
    """
    Verifica que ToolbarSeparator hereda de QFrame.
    """

    assert isinstance(separator, QFrame)


def test_toolbar_separator_object_name(separator):
    """
    Verifica que el objectName se configura correctamente.
    """

    assert separator.objectName() == "toolbar_separator"


def test_toolbar_separator_frame_shape(separator):
    """
    Verifica que el separador utiliza una línea vertical.
    """

    assert separator.frameShape() == QFrame.Shape.VLine


def test_toolbar_separator_frame_shadow(separator):
    """
    Verifica que el separador utiliza una sombra plana.
    """

    assert separator.frameShadow() == QFrame.Shadow.Plain

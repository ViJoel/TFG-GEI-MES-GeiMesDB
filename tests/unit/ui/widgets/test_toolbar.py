import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QWidget

from ui.widgets.workspace.sql_editor.toolbar import Toolbar
from ui.widgets.workspace.sql_editor.toolbar_button import ToolbarButton

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def toolbar(qtbot):
    """
    Construye un Toolbar de prueba.
    """

    widget = Toolbar()

    qtbot.addWidget(widget)

    return widget


# =============================================================================
# INITIALIZATION
# =============================================================================


def test_toolbar_is_qwidget(toolbar):
    """
    Verifica que Toolbar hereda de QWidget.
    """

    assert isinstance(toolbar, QWidget)


def test_toolbar_object_name(toolbar):
    """
    Verifica que el objectName se configura correctamente.
    """

    assert toolbar.objectName() == "toolbar"


def test_toolbar_has_execute_button(toolbar):
    """
    Verifica que el botón de ejecutar consulta se crea correctamente.
    """

    assert isinstance(toolbar.execute_button, ToolbarButton)


def test_toolbar_has_execute_script_button(toolbar):
    """
    Verifica que el botón de ejecutar script se crea correctamente.
    """

    assert isinstance(toolbar.execute_script_button, ToolbarButton)


def test_toolbar_has_undo_button(toolbar):
    """
    Verifica que el botón de deshacer se crea correctamente.
    """

    assert isinstance(toolbar.undo_button, ToolbarButton)


def test_toolbar_has_redo_button(toolbar):
    """
    Verifica que el botón de rehacer se crea correctamente.
    """

    assert isinstance(toolbar.redo_button, ToolbarButton)


def test_toolbar_has_layout(toolbar):
    """
    Verifica que la toolbar dispone de un layout.
    """

    assert toolbar.layout() is not None


# =============================================================================
# SIGNALS
# =============================================================================


def test_execute_query_requested_signal(toolbar, qtbot):
    """
    Verifica que pulsar Execute emite la señal correspondiente.
    """

    with qtbot.waitSignal(toolbar.execute_query_requested):
        QTest.mouseClick(
            toolbar.execute_button,
            Qt.MouseButton.LeftButton,
        )


def test_execute_script_requested_signal(toolbar, qtbot):
    """
    Verifica que pulsar Execute script emite la señal correspondiente.
    """

    with qtbot.waitSignal(toolbar.execute_script_requested):
        QTest.mouseClick(
            toolbar.execute_script_button,
            Qt.MouseButton.LeftButton,
        )


def test_undo_requested_signal(toolbar, qtbot):
    """
    Verifica que pulsar Undo emite la señal correspondiente.
    """

    with qtbot.waitSignal(toolbar.undo_requested):
        QTest.mouseClick(
            toolbar.undo_button,
            Qt.MouseButton.LeftButton,
        )


def test_redo_requested_signal(toolbar, qtbot):
    """
    Verifica que pulsar Redo emite la señal correspondiente.
    """

    with qtbot.waitSignal(toolbar.redo_requested):
        QTest.mouseClick(
            toolbar.redo_button,
            Qt.MouseButton.LeftButton,
        )

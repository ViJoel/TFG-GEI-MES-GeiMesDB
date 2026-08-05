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


def test_toolbar_has_execute_selection_button(toolbar):
    """
    Verifica que el botón de ejecutar selección se crea correctamente.
    """

    assert isinstance(toolbar.execute_selection_button, ToolbarButton)


def test_toolbar_has_execute_query_button(toolbar):
    """
    Verifica que el botón de ejecutar consulta se crea correctamente.
    """

    assert isinstance(toolbar.execute_query_button, ToolbarButton)


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


def test_toolbar_has_new_file_button(toolbar):
    """
    Verifica que el botón de nuevo archivo se crea correctamente.
    """

    assert isinstance(toolbar.new_button, ToolbarButton)


def test_toolbar_has_open_file_button(toolbar):
    """
    Verifica que el botón de abrir archivo se crea correctamente.
    """

    assert isinstance(toolbar.open_button, ToolbarButton)


def test_toolbar_has_save_file_button(toolbar):
    """
    Verifica que el botón de guardar archivo se crea correctamente.
    """

    assert isinstance(toolbar.save_button, ToolbarButton)


def test_toolbar_has_rename_file_button(toolbar):
    """
    Verifica que el botón de renombrar archivo se crea correctamente.
    """

    assert isinstance(toolbar.rename_button, ToolbarButton)


# =============================================================================
# BUTTONS
# =============================================================================


def test_set_buttons_text(toolbar):
    """
    Verifica que se actualizan los textos de los botones.
    """

    toolbar._set_buttons_text()

    assert toolbar.execute_selection_button.text() == toolbar.tr("Selection")
    assert toolbar.execute_query_button.text() == toolbar.tr("Query")
    assert toolbar.execute_script_button.text() == toolbar.tr("Script")
    assert toolbar.undo_button.text() == toolbar.tr("Undo")
    assert toolbar.redo_button.text() == toolbar.tr("Redo")
    assert toolbar.new_button.text() == toolbar.tr("New")
    assert toolbar.open_button.text() == toolbar.tr("Open")
    assert toolbar.save_button.text() == toolbar.tr("Save")
    assert toolbar.rename_button.text() == toolbar.tr("Rename")


# =============================================================================
# TOOLTIPS
# =============================================================================


def test_toolbar_buttons_have_tooltips(toolbar):
    """
    Verifica que todos los botones tienen texto de ayuda configurado.
    """

    buttons = [
        toolbar.execute_selection_button,
        toolbar.execute_query_button,
        toolbar.execute_script_button,
        toolbar.undo_button,
        toolbar.redo_button,
        toolbar.new_button,
        toolbar.open_button,
        toolbar.save_button,
        toolbar.rename_button,
    ]

    for button in buttons:
        assert button.toolTip() != ""


def test_toolbar_buttons_have_expected_tooltips(toolbar):
    """
    Verifica que los botones tienen los textos de ayuda esperados.
    """

    assert "Execute the text selected" in toolbar.execute_selection_button.toolTip()
    assert (
        "Execute the query under the cursor" in toolbar.execute_query_button.toolTip()
    )
    assert "Execute the full script" in toolbar.execute_script_button.toolTip()
    assert "Undo action on the text" in toolbar.undo_button.toolTip()
    assert "Redo action on the text" in toolbar.redo_button.toolTip()
    assert "Create a new file" in toolbar.new_button.toolTip()
    assert "Open a file from your computer" in toolbar.open_button.toolTip()
    assert "Save the file changes" in toolbar.save_button.toolTip()
    assert "Rename the file" in toolbar.rename_button.toolTip()


# =============================================================================
# SIGNALS
# =============================================================================


def test_execute_selection_requested_signal(toolbar, qtbot):
    """
    Verifica que pulsar Execute selection emite la señal correspondiente.
    """

    with qtbot.waitSignal(toolbar.execute_selection_requested):
        QTest.mouseClick(
            toolbar.execute_selection_button,
            Qt.MouseButton.LeftButton,
        )


def test_execute_query_requested_signal(toolbar, qtbot):
    """
    Verifica que pulsar Execute query emite la señal correspondiente.
    """

    with qtbot.waitSignal(toolbar.execute_query_requested):
        QTest.mouseClick(
            toolbar.execute_query_button,
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


def test_new_file_requested_signal(toolbar, qtbot):
    """
    Verifica que pulsar New file emite la señal correspondiente.
    """

    with qtbot.waitSignal(toolbar.new_file_requested):
        QTest.mouseClick(
            toolbar.new_button,
            Qt.MouseButton.LeftButton,
        )


def test_open_file_requested_signal(toolbar, qtbot):
    """
    Verifica que pulsar Open file emite la señal correspondiente.
    """

    with qtbot.waitSignal(toolbar.open_file_requested):
        QTest.mouseClick(
            toolbar.open_button,
            Qt.MouseButton.LeftButton,
        )


def test_save_file_requested_signal(toolbar, qtbot):
    """
    Verifica que pulsar Save file emite la señal correspondiente.
    """

    with qtbot.waitSignal(toolbar.save_file_requested):
        QTest.mouseClick(
            toolbar.save_button,
            Qt.MouseButton.LeftButton,
        )


def test_rename_file_requested_signal(toolbar, qtbot):
    """
    Verifica que pulsar Rename file emite la señal correspondiente.
    """

    with qtbot.waitSignal(toolbar.rename_file_requested):
        QTest.mouseClick(
            toolbar.rename_button,
            Qt.MouseButton.LeftButton,
        )


# =============================================================================
# TRANSLATIONS
# =============================================================================


def test_retranslate_ui(toolbar):
    """
    Verifica que se actualizan todos los textos traducibles.
    """

    toolbar._retranslate_ui()

    assert toolbar.execute_selection_button.text() == toolbar.tr("Selection")
    assert toolbar.execute_query_button.text() == toolbar.tr("Query")
    assert toolbar.execute_script_button.text() == toolbar.tr("Script")

    assert "Execute the text selected" in toolbar.execute_selection_button.toolTip()
    assert (
        "Execute the query under the cursor" in toolbar.execute_query_button.toolTip()
    )

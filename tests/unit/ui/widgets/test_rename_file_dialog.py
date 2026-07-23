from unittest.mock import patch

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QInputDialog,
    QWidget,
)

from ui.widgets.workspace.sql_editor.rename_file_dialog import (
    RenameFileDialog,
)

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def dialog(qtbot):
    """
    Construye un RenameFileDialog de prueba.
    """

    widget = RenameFileDialog(
        "test.sql",
    )

    qtbot.addWidget(widget)

    return widget


@pytest.fixture
def parent_widget(qtbot):
    """
    Construye un widget padre visible de prueba.
    """

    widget = QWidget()

    widget.resize(
        800,
        600,
    )

    widget.show()

    qtbot.addWidget(widget)

    return widget


# =============================================================================
# INITIALIZATION
# =============================================================================


def test_rename_file_dialog_is_qinputdialog(dialog):
    """
    Verifica que RenameFileDialog hereda de QInputDialog.
    """

    assert isinstance(dialog, QInputDialog)


def test_rename_file_dialog_stores_current_name(dialog):
    """
    Verifica que guarda el nombre actual del archivo.
    """

    assert dialog.current_name == "test.sql"


def test_rename_file_dialog_window_title(dialog):
    """
    Verifica que configura correctamente el título de la ventana.
    """

    assert dialog.windowTitle() == "Rename file"


def test_rename_file_dialog_label_text(dialog):
    """
    Verifica que configura correctamente el texto de la etiqueta.
    """

    assert dialog.labelText() == "New file name:"


def test_rename_file_dialog_initial_text_value(dialog):
    """
    Verifica que muestra el nombre actual como valor inicial.
    """

    assert dialog.textValue() == "test.sql"


def test_rename_file_dialog_has_dialog_flag(dialog):
    """
    Verifica que configura la ventana como diálogo.
    """

    assert dialog.windowFlags() & Qt.WindowType.Dialog


def test_rename_file_dialog_has_frameless_flag(dialog):
    """
    Verifica que elimina la barra de título nativa.
    """

    assert dialog.windowFlags() & Qt.WindowType.FramelessWindowHint


# =============================================================================
# BUTTONS
# =============================================================================


def test_setup_buttons_styles_without_button_box_does_not_fail(dialog):
    """
    Verifica que no falla al aplicar estilos sin botones disponibles.
    """

    dialog._setup_buttons_styles()


# =============================================================================
# SHOW EVENT
# =============================================================================


def test_show_event_applies_button_styles(dialog):
    """
    Verifica que aplica los estilos de botones al mostrar el diálogo.
    """

    with patch.object(
        dialog,
        "_setup_buttons_styles",
    ) as mocked:

        dialog.show()

        mocked.assert_called_once()


def test_show_event_centers_dialog_with_visible_parent(
    qtbot,
    parent_widget,
):
    """
    Verifica que centra el diálogo respecto al widget padre visible.
    """

    dialog = RenameFileDialog(
        "test.sql",
        parent_widget,
    )

    qtbot.addWidget(dialog)

    dialog.resize(
        300,
        200,
    )

    dialog.show()

    parent_position = parent_widget.mapToGlobal(
        parent_widget.geometry().topLeft(),
    )

    expected_x = parent_position.x() + (parent_widget.width() - dialog.width()) // 2

    expected_y = parent_position.y() + (parent_widget.height() - dialog.height()) // 2

    assert dialog.x() == expected_x
    assert dialog.y() == expected_y


# =============================================================================
# PUBLIC API
# =============================================================================


def test_get_new_name_returns_name_when_accepted():
    """
    Verifica que devuelve el nuevo nombre al aceptar el diálogo.
    """

    with patch.object(
        RenameFileDialog,
        "exec",
        return_value=QInputDialog.DialogCode.Accepted,
    ), patch.object(
        RenameFileDialog,
        "textValue",
        return_value="new_name.sql",
    ):

        result = RenameFileDialog.get_new_name(
            "old.sql",
        )

    assert result == "new_name.sql"


def test_get_new_name_strips_spaces():
    """
    Verifica que elimina espacios del nombre obtenido.
    """

    with patch.object(
        RenameFileDialog,
        "exec",
        return_value=QInputDialog.DialogCode.Accepted,
    ), patch.object(
        RenameFileDialog,
        "textValue",
        return_value="  new_name.sql  ",
    ):

        result = RenameFileDialog.get_new_name(
            "old.sql",
        )

    assert result == "new_name.sql"


def test_get_new_name_returns_none_when_name_is_empty():
    """
    Verifica que devuelve None cuando el nombre está vacío.
    """

    with patch.object(
        RenameFileDialog,
        "exec",
        return_value=QInputDialog.DialogCode.Accepted,
    ), patch.object(
        RenameFileDialog,
        "textValue",
        return_value="   ",
    ):

        result = RenameFileDialog.get_new_name(
            "old.sql",
        )

    assert result is None


def test_get_new_name_returns_none_when_dialog_is_cancelled():
    """
    Verifica que devuelve None al cancelar el diálogo.
    """

    with patch.object(
        RenameFileDialog,
        "exec",
        return_value=QInputDialog.DialogCode.Rejected,
    ):

        result = RenameFileDialog.get_new_name(
            "old.sql",
        )

    assert result is None

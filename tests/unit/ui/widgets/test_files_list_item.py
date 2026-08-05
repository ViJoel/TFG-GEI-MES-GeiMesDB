from pathlib import Path
from unittest.mock import MagicMock

import pytest
from PySide6.QtCore import (
    QSize,
    Qt,
)
from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QWidget,
)

from entities.file import File
from ui.widgets.workspace.sql_editor.files_list_item import (
    CloseFileButton,
    ElidedLabel,
    FilesListItem,
)

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def file():
    """
    Construye un archivo de prueba.
    """

    return File(
        path=Path("test.sql"),
        content="SELECT 1;",
    )


@pytest.fixture
def item(
    qtbot,
    file,
):
    """
    Construye un FilesListItem de prueba.
    """

    widget = FilesListItem(
        file,
    )

    qtbot.addWidget(widget)

    return widget


@pytest.fixture
def close_button(
    qtbot,
):
    """
    Construye un CloseFileButton de prueba.
    """

    widget = CloseFileButton()

    qtbot.addWidget(widget)

    return widget


@pytest.fixture
def label(
    qtbot,
):
    """
    Construye un ElidedLabel de prueba.
    """

    widget = ElidedLabel(
        "example text",
    )

    qtbot.addWidget(widget)

    return widget


# =============================================================================
# CLOSE FILE BUTTON
# =============================================================================


def test_close_file_button_is_push_button(close_button):
    """
    Verifica que CloseFileButton hereda de QPushButton.
    """

    assert isinstance(
        close_button,
        QPushButton,
    )


def test_close_file_button_object_name(close_button):
    """
    Verifica que configura correctamente el objectName.
    """

    assert close_button.objectName() == "files_list_item_close_button"


def test_close_file_button_fixed_size(close_button):
    """
    Verifica que tiene el tamaño fijo configurado.
    """

    assert close_button.size() == QSize(
        16,
        16,
    )


def test_close_file_button_size_policy(close_button):
    """
    Verifica que utiliza política de tamaño fijo.
    """

    assert close_button.sizePolicy().horizontalPolicy().name == "Fixed"
    assert close_button.sizePolicy().verticalPolicy().name == "Fixed"


def test_close_file_button_initial_state_uses_default_icon(
    close_button,
):
    """
    Verifica que el estado inicial utiliza el icono por defecto.
    """

    assert close_button._alternative_state is False
    assert close_button._current_icon() is close_button._icon_default


def test_close_file_button_alternative_state_enabled(
    close_button,
):
    """
    Verifica que activa el icono alternativo.
    """

    close_button.set_alternative_state(
        True,
    )

    assert close_button._alternative_state is True
    assert close_button._current_icon() is close_button._icon_alt


def test_close_file_button_alternative_state_disabled(
    close_button,
):
    """
    Verifica que restaura el icono por defecto.
    """

    close_button.set_alternative_state(
        True,
    )

    close_button.set_alternative_state(
        False,
    )

    assert close_button._alternative_state is False
    assert close_button._current_icon() is close_button._icon_default


def test_close_file_button_on_theme_changed_recreates_icons(
    close_button,
):
    """
    Verifica que un cambio de tema reconstruye los
    iconos y actualiza el icono mostrado.
    """

    close_button._create_icons = MagicMock()
    close_button.setIcon = MagicMock()
    close_button._current_icon = MagicMock()

    close_button._on_theme_changed(
        "dark",
    )

    close_button._create_icons.assert_called_once_with()

    close_button.setIcon.assert_called_once_with(
        close_button._current_icon.return_value,
    )


# =====================================
# INTERNATIONALIZATION
# =====================================


def test_close_file_button_retranslate_updates_tooltip(
    close_button,
):
    """
    Verifica que la interfaz actualiza correctamente
    el texto traducible del tooltip.
    """

    close_button._retranslate_ui()

    assert close_button.toolTip() == close_button.tr(
        "Close the editor tab.<br><br><b>Shortcut:</b> <code>Ctrl + W</code>"
    )


# =============================================================================
# ELIDED LABEL
# =============================================================================


def test_elided_label_is_label(label):
    """
    Verifica que ElidedLabel hereda de QLabel.
    """

    assert isinstance(
        label,
        QLabel,
    )


def test_elided_label_object_name(label):
    """
    Verifica que configura correctamente el objectName.
    """

    assert label.objectName() == "files_list_item_label"


def test_elided_label_stores_full_text(label):
    """
    Verifica que guarda el texto completo original.
    """

    assert label._full_text == "example text"


def test_elided_label_text_update(label):
    """
    Verifica que actualiza correctamente el texto completo.
    """

    label.setText(
        "new text",
    )

    assert label._full_text == "new text"
    assert label.text() == "new text"


def test_elided_label_minimum_size_hint(label):
    """
    Verifica que permite reducir el ancho mínimo.
    """

    size = label.minimumSizeHint()

    assert isinstance(
        size,
        QSize,
    )

    assert size.width() == 0


# =============================================================================
# FILES LIST ITEM
# =============================================================================


def test_files_list_item_is_widget(item):
    """
    Verifica que FilesListItem hereda de QWidget.
    """

    assert isinstance(
        item,
        QWidget,
    )


def test_files_list_item_stores_file(item, file):
    """
    Verifica que conserva el archivo asociado.
    """

    assert item.file is file


def test_files_list_item_object_name(item):
    """
    Verifica que configura correctamente el objectName.
    """

    assert item.objectName() == "files_list_item"


def test_files_list_item_has_file_name_label(item):
    """
    Verifica que crea la etiqueta del nombre del archivo.
    """

    assert isinstance(
        item.file_name_label,
        ElidedLabel,
    )


def test_files_list_item_displays_file_name(item):
    """
    Verifica que muestra el nombre del archivo.
    """

    assert item.file_name_label.text() == "test.sql"


def test_files_list_item_has_close_button(item):
    """
    Verifica que crea el botón de cierre.
    """

    assert isinstance(
        item.close_button,
        CloseFileButton,
    )


def test_files_list_item_close_signal(qtbot, item):
    """
    Verifica que emitir el cierre envía el propio widget.
    """

    with qtbot.waitSignal(
        item.close_requested,
    ) as signal:

        item.close_button.click()

    assert signal.args == [item]


def test_files_list_item_selected_true(item):
    """
    Verifica que aplica el estado seleccionado.
    """

    item.set_selected(
        True,
    )

    assert item.property("selected") == "true"


def test_files_list_item_selected_false(item):
    """
    Verifica que elimina el estado seleccionado.
    """

    item.set_selected(
        False,
    )

    assert item.property("selected") == "false"


def test_files_list_item_refresh_updates_name(item):
    """
    Verifica que actualiza el nombre mostrado.
    """

    item.file.name = "changed.sql"

    item.refresh()

    assert item.file_name_label.text() == "changed.sql"


def test_files_list_item_refresh_updates_close_button_state(
    item,
):
    """
    Verifica que actualiza el estado del botón de cierre.
    """

    item.file.content = "CHANGED"

    item.refresh()

    assert item.close_button._alternative_state is True
    assert item.close_button._current_icon() is item.close_button._icon_alt

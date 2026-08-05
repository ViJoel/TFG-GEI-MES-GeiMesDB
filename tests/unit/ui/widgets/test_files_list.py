from pathlib import Path

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QListWidget,
    QSizePolicy,
)

from entities.file import File
from ui.widgets.workspace.sql_editor.files_list import FilesList
from ui.widgets.workspace.sql_editor.files_list_item import FilesListItem

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def files_list(
    qtbot,
):
    """
    Construye una FilesList de prueba.
    """

    widget = FilesList()

    qtbot.addWidget(widget)

    return widget


@pytest.fixture
def file_one():
    """
    Construye el primer archivo de prueba.
    """

    return File(
        path=Path("first.sql"),
        content="SELECT 1;",
    )


@pytest.fixture
def file_two():
    """
    Construye el segundo archivo de prueba.
    """

    return File(
        path=Path("second.sql"),
        content="SELECT 2;",
    )


# =============================================================================
# INITIALIZATION
# =============================================================================


def test_files_list_is_list_widget(files_list):
    """
    Verifica que FilesList hereda de QListWidget.
    """

    assert isinstance(
        files_list,
        QListWidget,
    )


def test_files_list_object_name(files_list):
    """
    Verifica que configura correctamente el objectName.
    """

    assert files_list.objectName() == "files_list"


def test_files_list_spacing(files_list):
    """
    Verifica que configura el espaciado entre elementos.
    """

    assert files_list.spacing() == 2


def test_files_list_vertical_scroll_mode(files_list):
    """
    Verifica que configura el modo de scroll vertical.
    """

    assert files_list.verticalScrollMode() == files_list.ScrollMode.ScrollPerPixel


def test_files_list_horizontal_scroll_mode(files_list):
    """
    Verifica que configura el modo de scroll horizontal.
    """

    assert files_list.horizontalScrollMode() == files_list.ScrollMode.ScrollPerPixel


def test_files_list_scroll_speed(files_list):
    """
    Verifica que configura la velocidad de desplazamiento.
    """

    assert files_list.verticalScrollBar().singleStep() == 10
    assert files_list.horizontalScrollBar().singleStep() == 10


def test_files_list_has_no_focus(files_list):
    """
    Verifica que elimina el foco de teclado.
    """

    assert files_list.focusPolicy() == Qt.FocusPolicy.NoFocus


def test_files_list_size_policy(files_list):
    """
    Verifica que permite expandirse en ambas direcciones.
    """

    assert files_list.sizePolicy().horizontalPolicy() == QSizePolicy.Policy.Expanding

    assert files_list.sizePolicy().verticalPolicy() == QSizePolicy.Policy.Expanding


def test_files_list_minimum_width(files_list):
    """
    Verifica que tiene un ancho mínimo configurado.
    """

    assert files_list.minimumWidth() == 200


# =============================================================================
# ADD FILE
# =============================================================================


def test_add_file_adds_item(
    files_list,
    file_one,
):
    """
    Verifica que añade un archivo a la lista.
    """

    files_list.add_file(
        file_one,
    )

    assert files_list.count() == 1


def test_add_file_creates_files_list_item(
    files_list,
    file_one,
):
    """
    Verifica que crea la representación visual del archivo.
    """

    files_list.add_file(
        file_one,
    )

    item = files_list.item(0)

    widget = files_list.itemWidget(item)

    assert isinstance(
        widget,
        FilesListItem,
    )


def test_add_file_selects_added_item(
    files_list,
    file_one,
):
    """
    Verifica que selecciona el archivo añadido.
    """

    files_list.add_file(
        file_one,
    )

    assert files_list.currentRow() == 0


# =============================================================================
# REMOVE FILE
# =============================================================================


def test_remove_file_removes_existing_file(
    files_list,
    file_one,
):
    """
    Verifica que elimina un archivo existente.
    """

    files_list.add_file(
        file_one,
    )

    files_list.remove_file(
        file_one,
    )

    assert files_list.count() == 0


def test_remove_file_keeps_other_files(
    files_list,
    file_one,
    file_two,
):
    """
    Verifica que mantiene el resto de archivos.
    """

    files_list.add_file(file_one)
    files_list.add_file(file_two)

    files_list.remove_file(file_one)

    assert files_list.count() == 1


def test_remove_file_ignores_unknown_file(
    files_list,
    file_one,
):
    """
    Verifica que no elimina archivos no existentes.
    """

    other_file = File()

    files_list.add_file(
        file_one,
    )

    files_list.remove_file(
        other_file,
    )

    assert files_list.count() == 1


# =============================================================================
# SELECTION
# =============================================================================


def test_select_first_file_selects_first_item(
    files_list,
    file_one,
    file_two,
):
    """
    Verifica que selecciona el primer archivo.
    """

    files_list.add_file(file_one)
    files_list.add_file(file_two)

    files_list.select_first_file()

    assert files_list.currentRow() == 0


def test_select_first_file_without_items_does_nothing(
    files_list,
):
    """
    Verifica que no falla con una lista vacía.
    """

    files_list.select_first_file()

    assert files_list.currentRow() == -1


def test_file_selected_signal_is_emitted_when_selection_changes(
    qtbot,
    files_list,
    file_one,
    file_two,
):
    """
    Verifica que emite la señal al cambiar la selección.
    """

    files_list.add_file(
        file_one,
    )

    with qtbot.waitSignal(
        files_list.file_selected,
    ) as signal:

        files_list.add_file(
            file_two,
        )

    assert signal.args == [file_two]


# =============================================================================
# CLOSE SIGNAL
# =============================================================================


def test_file_close_requested_signal_is_emitted(
    qtbot,
    files_list,
    file_one,
):
    """
    Verifica que propaga la solicitud de cierre.
    """

    files_list.add_file(
        file_one,
    )

    item = files_list.item(0)

    widget = files_list.itemWidget(item)

    with qtbot.waitSignal(
        files_list.file_close_requested,
    ) as signal:

        widget.close_button.click()

    assert signal.args == [file_one]


# =============================================================================
# REFRESH
# =============================================================================


def test_refresh_file_updates_widget(
    files_list,
    file_one,
):
    """
    Verifica que actualiza la representación visual.
    """

    files_list.add_file(
        file_one,
    )

    file_one.name = "changed.sql"

    files_list.refresh_file(
        file_one,
    )

    widget = files_list.itemWidget(
        files_list.item(0),
    )

    assert widget.file_name_label.text() == "changed.sql"


def test_refresh_unknown_file_does_nothing(
    files_list,
    file_one,
):
    """
    Verifica que no falla con archivos inexistentes.
    """

    files_list.add_file(
        file_one,
    )

    files_list.refresh_file(
        File(),
    )

    assert files_list.count() == 1


# =============================================================================
# SORT
# =============================================================================


def test_sort_list_orders_items_alphabetically(
    files_list,
):
    """
    Verifica que ordena los archivos alfabéticamente.
    """

    file_b = File(
        path=Path("b.sql"),
    )

    file_a = File(
        path=Path("a.sql"),
    )

    files_list.add_file(file_b)
    files_list.add_file(file_a)

    files_list._sort_list()

    first_widget = files_list.itemWidget(
        files_list.item(0),
    )

    second_widget = files_list.itemWidget(
        files_list.item(1),
    )

    assert first_widget.file.name == "a.sql"
    assert second_widget.file.name == "b.sql"


def test_update_items_selection_state_updates_selection(
    files_list,
    file_one,
    file_two,
):
    """
    Verifica que actualiza el estado visual de selección.
    """

    files_list.add_file(file_one)
    files_list.add_file(file_two)

    files_list.setCurrentRow(1)

    files_list._update_items_selection_state()

    first = files_list.itemWidget(
        files_list.item(0),
    )

    second = files_list.itemWidget(
        files_list.item(1),
    )

    assert first.property("selected") == "false"
    assert second.property("selected") == "true"

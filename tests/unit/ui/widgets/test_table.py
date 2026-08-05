from unittest.mock import (
    MagicMock,
    patch,
)

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent

from ui.widgets.workspace.results_view.result_table_model import ResultTableModel
from ui.widgets.workspace.results_view.table import Table

# =============================================================================
# FIXTURE
# =============================================================================


@pytest.fixture
def table(qtbot):
    """
    Crea instancia de Table.
    """

    widget = Table()
    qtbot.addWidget(widget)

    return widget


@pytest.fixture
def result_set():
    """
    ResultSet simulado.
    """

    rs = MagicMock()
    rs.columns = ["id", "name"]
    rs.columns_types = [int, str]
    rs.rows = [[1, "Alice"]]

    return rs


@pytest.fixture(autouse=True)
def patch_model():
    """
    Evita dependencias reales del ResultTableModel.
    """

    with patch(
        "ui.widgets.workspace.results_view.table.ResultTableModel"
    ) as mock_model:
        yield mock_model


# =============================================================================
# INIT / STATE
# =============================================================================


def test_initial_state(table):
    """
    Verifica estado inicial del widget.
    """

    assert table.model is None
    assert table.objectName() == "table"


# =============================================================================
# SET RESULT SET
# =============================================================================


def test_set_result_set_creates_model(table, result_set, patch_model):
    """
    Verifica creación del modelo sin depender de Qt internals.
    """

    model_instance = MagicMock()
    patch_model.return_value = model_instance

    table.setModel = MagicMock()

    table.set_result_set(result_set)

    patch_model.assert_called_once_with(result_set)

    model_instance.state_changed.connect.assert_called_once()

    table.setModel.assert_called_once_with(model_instance)

    assert table.model == model_instance


# =============================================================================
# DISCARD CHANGES
# =============================================================================


def test_discard_changes_when_model_exists(table):
    """
    Verifica que se delega discard_changes al modelo.
    """

    table.model = MagicMock()

    table.discard_changes()

    table.model.discard_changes.assert_called_once()


def test_discard_changes_when_model_none(table):
    """
    Verifica que no falla si no hay modelo.
    """

    table.model = None

    table.discard_changes()  # no debe lanzar excepción


# =============================================================================
# SET EDITABLE
# =============================================================================


def test_set_editable_true_sets_triggers(table):
    """
    Verifica modo editable.
    """

    table.setEditTriggers = MagicMock()

    table.set_editable(True)

    table.setEditTriggers.assert_called_once()


def test_set_editable_false_disables_editing(table):
    """
    Verifica modo no editable.
    """

    table.setEditTriggers = MagicMock()

    table.set_editable(False)

    table.setEditTriggers.assert_called_once()


# =============================================================================
# KEY PRESS EVENT
# =============================================================================


def test_key_press_copy_copies_current_cell(
    table,
    mocker,
):
    """
    Verifica que Ctrl+C copia el valor de la celda
    seleccionada al portapapeles.
    """

    index = mocker.Mock()
    index.isValid.return_value = True
    index.data.return_value = "Alice"

    table.currentIndex = mocker.Mock(return_value=index)

    clipboard = mocker.Mock()

    mocker.patch(
        "ui.widgets.workspace.results_view.table.QApplication.clipboard",
        return_value=clipboard,
    )

    event = QKeyEvent(
        QKeyEvent.KeyPress,
        Qt.Key_C,
        Qt.ControlModifier,
    )

    table.keyPressEvent(event)

    clipboard.setText.assert_called_once_with("Alice")
    assert event.isAccepted()


def test_key_press_copy_without_valid_index_calls_super(
    table,
    mocker,
):
    """
    Verifica que Ctrl+C sin una celda válida delega
    el procesamiento en QTableView.
    """

    index = mocker.Mock()
    index.isValid.return_value = False

    table.currentIndex = mocker.Mock(return_value=index)

    super_event = mocker.patch(
        "PySide6.QtWidgets.QTableView.keyPressEvent",
    )

    event = QKeyEvent(
        QKeyEvent.KeyPress,
        Qt.Key_C,
        Qt.ControlModifier,
    )

    table.keyPressEvent(event)

    super_event.assert_called_once()


def test_key_press_enter_starts_editing(
    table,
    mocker,
):
    """
    Verifica que Enter inicia la edición de la celda
    seleccionada.
    """

    index = mocker.Mock()

    table.currentIndex = mocker.Mock(return_value=index)
    table.edit = mocker.Mock()

    event = QKeyEvent(
        QKeyEvent.KeyPress,
        Qt.Key_Return,
        Qt.NoModifier,
    )

    table.keyPressEvent(event)

    table.edit.assert_called_once_with(index)
    assert event.isAccepted()


def test_key_press_other_key_calls_super(
    table,
    mocker,
):
    """
    Verifica que cualquier otra tecla se delega a la
    implementación base.
    """

    super_event = mocker.patch(
        "PySide6.QtWidgets.QTableView.keyPressEvent",
    )

    event = QKeyEvent(
        QKeyEvent.KeyPress,
        Qt.Key_A,
        Qt.NoModifier,
    )

    table.keyPressEvent(event)

    super_event.assert_called_once()

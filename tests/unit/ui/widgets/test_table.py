from unittest.mock import (
    MagicMock,
    patch,
)

import pytest

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

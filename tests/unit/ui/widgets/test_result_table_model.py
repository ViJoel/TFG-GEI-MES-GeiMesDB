from datetime import (
    date,
    datetime,
    time,
)
from decimal import Decimal
from unittest.mock import (
    MagicMock,
    patch,
)

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from entities.query_result import ResultSet
from ui.widgets.workspace.results_view.result_table_model import ResultTableModel

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def result_set():
    """
    Crea un ResultSet mínimo para pruebas.
    """

    rs = MagicMock(spec=ResultSet)
    rs.columns = ["id", "name", "active"]
    rs.rows = [
        [1, "Alice", True],
        [2, "Bob", False],
    ]
    rs.table_metadata = MagicMock()
    rs.table_metadata.primary_key_columns = ["id"]
    rs.table_metadata.convert_value = MagicMock()

    return rs


@pytest.fixture
def model(result_set):
    """
    Crea el modelo ResultTableModel.
    """

    return ResultTableModel(result_set)


@pytest.fixture(autouse=True)
def patch_theme_manager():
    with (
        patch(
            "ui.widgets.workspace.results_view.result_table_model.ThemeManager.get_color",
            return_value="#FFFFFF",
        ),
        patch(
            "ui.widgets.workspace.results_view.result_table_model.ThemeManager.get_qcolor",
            return_value=QColor("#FFFFFF"),
        ),
    ):
        yield


# =============================================================================
# ROW / COLUMN COUNT
# =============================================================================


def test_row_count(model):
    """
    Verifica que rowCount devuelve el número correcto de filas.
    """

    assert model.rowCount() == 2


def test_column_count(model):
    """
    Verifica que columnCount devuelve el número correcto de columnas.
    """

    assert model.columnCount() == 3


# =============================================================================
# DATA
# =============================================================================


def test_data_display_role(model):
    """
    Verifica que data devuelve valores correctos para DisplayRole.
    """

    index = model.index(0, 1)

    assert model.data(index, Qt.DisplayRole) == "Alice"


def test_data_edit_role(model):
    """
    Verifica que data devuelve valores correctos para EditRole.
    """

    index = model.index(1, 0)

    assert model.data(index, Qt.EditRole) == "2"


def test_data_modified_cell_background_role(model):
    """
    Verifica que una celda modificada devuelve color de fondo.
    """

    index = model.index(0, 0)

    model.modified_cells.add((0, 0))

    result = model.data(index, Qt.BackgroundRole)

    assert result is not None


def test_data_modified_cell_foreground_role(model):
    """
    Verifica que una celda modificada devuelve color de texto.
    """

    index = model.index(0, 0)

    model.modified_cells.add((0, 0))

    result = model.data(index, Qt.ForegroundRole)

    assert result is not None


# =============================================================================
# HEADER DATA
# =============================================================================


def test_header_data_horizontal(model):
    """
    Verifica que headerData devuelve nombres de columnas.
    """

    assert model.headerData(1, Qt.Horizontal, Qt.DisplayRole) == "name"


# =============================================================================
# FLAGS
# =============================================================================


def test_flags_returns_editable(model):
    """
    Verifica que las celdas son editables.
    """

    index = model.index(0, 0)

    flags = model.flags(index)

    assert flags & Qt.ItemIsEditable


# =============================================================================
# SET DATA
# =============================================================================


def test_set_data_modifies_value(model):
    """
    Verifica que setData modifica correctamente una celda.
    """

    index = model.index(0, 1)

    model._convert_value = MagicMock(return_value="AliceUpdated")
    model._modify_cell_value = MagicMock()

    result = model.setData(index, "AliceUpdated", Qt.EditRole)

    assert result is True

    model._convert_value.assert_called_once()
    model._modify_cell_value.assert_called_once()


def test_set_data_wrong_role_returns_false(model):
    """
    Verifica que setData rechaza roles no EditRole.
    """

    index = model.index(0, 1)

    result = model.setData(index, "Alice", Qt.DisplayRole)

    assert result is False


# =============================================================================
# HAS CHANGES
# =============================================================================


def test_has_changes_true(model):
    """
    Verifica que el modelo detecta cambios cuando existen
    celdas modificadas.
    """

    model.modified_cells.add((0, 0))

    assert model._has_changes() is True


def test_has_changes_false(model):
    """
    Verifica que el modelo detecta ausencia de cambios
    cuando no hay celdas modificadas.
    """

    assert model._has_changes() is False


# =============================================================================
# DISCARD CHANGES
# =============================================================================


def test_discard_changes(model):
    """
    Verifica que discard_changes restaura estado.
    """

    model.modified_cells.add((0, 0))

    model.layoutChanged = MagicMock()
    model.state_changed = MagicMock()

    model.discard_changes()

    assert model.modified_cells == set()

    model.layoutChanged.emit.assert_called_once()
    model.state_changed.emit.assert_called_once_with(False)


# =============================================================================
# MODIFY CELL VALUE
# =============================================================================


def test_modify_cell_value_adds_modified_cell(model):
    """
    Verifica que una celda distinta al original se marca como modificada.
    """

    model.result_set.rows[0][1] = "Alice"
    model.original_result_set.rows[0][1] = "AliceOriginal"

    model.state_changed = MagicMock()

    model._modify_cell_value(
        row=0,
        column=1,
        original_value="AliceOriginal",
        new_value="AliceModified",
    )

    assert (0, 1) in model.modified_cells

    model.state_changed.emit.assert_called_once()


def test_modify_cell_value_removes_modified_cell_when_equal(model):
    """
    Verifica que si el valor vuelve al original se elimina de modified_cells.
    """

    model.modified_cells.add((0, 1))

    model.state_changed = MagicMock()

    model._modify_cell_value(
        row=0,
        column=1,
        original_value="Alice",
        new_value="Alice",
    )

    assert (0, 1) not in model.modified_cells

    model.state_changed.emit.assert_called_once()


# =============================================================================
# CONVERT VALUE
# =============================================================================


def test_convert_value_delegates_to_table_metadata(model):
    """
    Verifica que la conversión se delega al TableMetadata.
    """

    model.result_set.table_metadata.convert_value.return_value = 123

    result = model._convert_value(
        column=0,
        value="123",
    )

    assert result == 123

    model.result_set.table_metadata.convert_value.assert_called_once_with(
        column_name="id",
        value="123",
    )


def test_value_to_str_none(model):
    assert model._value_to_str(None) == "[NULL]"


def test_value_to_str_decimal(model):
    assert model._value_to_str(Decimal("10.5")) == "10.5"


def test_value_to_str_date(model):
    assert model._value_to_str(date(2024, 1, 1)) == "2024-01-01"


def test_value_to_str_datetime(model):
    value = datetime(2024, 1, 1, 12, 0)

    assert model._value_to_str(value) == value.isoformat()


def test_value_to_str_time(model):
    value = time(12, 30)

    assert model._value_to_str(value) == value.isoformat()


def test_value_to_str_dict(model):
    assert model._value_to_str({"a": 1}) == '{"a": 1}'


# =============================================================================
# GENERATE UPDATE OPERATIONS
# =============================================================================


def test_generate_update_operations(model):
    """
    Verifica que se genera una operación UPDATE.
    """

    model.modified_cells = {(0, 1)}

    operations = model.generate_update_operations()

    assert len(operations) == 1

    operation = operations[0]

    assert operation.primary_key == {"id": 1}
    assert operation.values == {"name": "Alice"}
    assert operation.table_metadata is model.result_set.table_metadata


def test_generate_update_operations_multiple_rows(model):
    model.modified_cells = {
        (0, 1),
        (1, 1),
    }

    operations = model.generate_update_operations()

    assert len(operations) == 2


def test_generate_update_operations_multiple_columns(model):
    model.modified_cells = {
        (0, 1),
        (0, 2),
    }

    operations = model.generate_update_operations()

    assert len(operations) == 1

    assert operations[0].values == {
        "name": "Alice",
        "active": True,
    }


# =============================================================================
# GET TABLE CELL COLOR
# =============================================================================


def test_get_table_cell_color_invalid_role_returns_none(model):
    """
    Verifica que los roles no soportados devuelven None.
    """

    assert (
        model._get_table_cell_color(
            row=0,
            column=0,
            role=Qt.DisplayRole,
        )
        is None
    )


def test_get_table_cell_color_modified_background(model):
    """
    Verifica que una celda modificada devuelve el color
    de fondo configurado por el tema.
    """

    model.modified_cells.add((0, 0))

    with patch(
        "ui.widgets.workspace.results_view.result_table_model.ThemeManager.get_qcolor"
    ) as get_qcolor:

        color = QColor("#FFFFFF")
        get_qcolor.return_value = color

        result = model._get_table_cell_color(
            row=0,
            column=0,
            role=Qt.BackgroundRole,
        )

        assert result is color

        get_qcolor.assert_called_once_with(
            key="table_cell_modified_background_color",
            alpha=64,
        )


def test_get_table_cell_color_modified_foreground(model):
    """
    Verifica que el color de texto de una celda modificada
    sigue resolviéndose según el tipo de dato.
    """

    model.modified_cells.add((0, 1))

    result = model._get_table_cell_color(
        row=0,
        column=1,
        role=Qt.ForegroundRole,
    )

    assert isinstance(result, QColor)


def test_get_table_cell_color_background_returns_none(model):
    """
    Verifica que una celda no modificada no define
    color de fondo.
    """

    assert (
        model._get_table_cell_color(
            row=0,
            column=0,
            role=Qt.BackgroundRole,
        )
        is None
    )


@pytest.mark.parametrize(
    ("value", "theme_key"),
    [
        (None, "table_null_color"),
        (True, "table_boolean_color"),
        (123, "table_number_color"),
        (1.5, "table_number_color"),
        (Decimal("10.5"), "table_number_color"),
        ("hello", "table_string_color"),
        (date(2024, 1, 1), "table_datetime_color"),
        (datetime(2024, 1, 1, 10, 0), "table_datetime_color"),
        (time(10, 30), "table_datetime_color"),
        ({"a": 1}, "table_json_color"),
        (object(), "table_default_color"),
    ],
)
def test_get_table_cell_color_foreground_by_value_type(
    model,
    value,
    theme_key,
):
    """
    Verifica que el color de primer plano se obtiene
    utilizando la clave del tema correspondiente al
    tipo de dato de la celda.
    """

    model.result_set.rows[0][0] = value

    with patch(
        "ui.widgets.workspace.results_view.result_table_model.ThemeManager.get_color",
        return_value="#FFFFFF",
    ) as get_color:

        result = model._get_table_cell_color(
            row=0,
            column=0,
            role=Qt.ForegroundRole,
        )

        assert isinstance(result, QColor)

        get_color.assert_called_once_with(theme_key)

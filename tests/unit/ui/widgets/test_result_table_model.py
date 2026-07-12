from datetime import (
    date,
    datetime,
)
from decimal import Decimal
from unittest.mock import (
    MagicMock,
    patch,
)

import pytest
from PySide6.QtCore import Qt

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
    rs.columns_types = [int, str, bool]
    rs.rows = [
        [1, "Alice", True],
        [2, "Bob", False],
    ]
    rs.primary_key_columns = ["id"]
    rs.table_name = "users"

    return rs


@pytest.fixture
def model(result_set):
    """
    Crea el modelo ResultTableModel.
    """

    return ResultTableModel(result_set)


@pytest.fixture(autouse=True)
def patch_theme_manager():
    """
    Evita dependencia del ThemeManager real.
    """

    with patch(
        "ui.widgets.workspace.results_view.result_table_model.ThemeManager.get_color",
        return_value="#FFFFFF",
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

    assert model.data(index, Qt.EditRole) == 2


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
# CONVERT VALUE
# =============================================================================


def test_convert_value_int(model):
    """
    Verifica conversión de string a entero.
    """

    assert model._convert_value(0, "123") == 123


def test_convert_value_float(model):
    """
    Verifica conversión de string a float según tipo de columna.
    """

    model.result_set.columns_types[0] = float
    assert model._convert_value(0, "1.5") == 1.5


def test_convert_value_bool(model):
    """
    Verifica conversión de string a booleano.
    """

    model.result_set.columns_types[0] = bool
    assert model._convert_value(0, "true") is True


def test_convert_value_decimal(model):
    """
    Verifica conversión de string a Decimal.
    """

    model.result_set.columns_types[0] = Decimal
    assert model._convert_value(0, "10.5") == Decimal("10.5")


def test_convert_value_date(model):
    """
    Verifica conversión de string a date en formato ISO.
    """

    model.result_set.columns_types[0] = date
    assert model._convert_value(0, "2024-01-01") == date(2024, 1, 1)


def test_convert_value_datetime(model):
    """
    Verifica conversión de string a datetime desde ISO format.
    """

    model.result_set.columns_types[0] = datetime
    assert model._convert_value(0, "2024-01-01T10:00:00") == datetime.fromisoformat(
        "2024-01-01T10:00:00"
    )


def test_convert_value_str_column_type_returns_value(model):
    """
    Verifica que columnas tipo str devuelven el valor sin transformación.
    """

    model.result_set.columns_types[0] = str

    result = model._convert_value(0, "hello world")

    assert result == "hello world"


# =============================================================================
# CONVERT VALUE (EDGE CASES)
# =============================================================================


def test_convert_value_empty_string_returns_none(model):
    """
    Verifica que string vacío devuelve None.
    """

    assert model._convert_value(0, "") is None


def test_convert_value_unknown_type_returns_value(model):
    """
    Verifica que tipos desconocidos devuelven el valor original.
    """

    class CustomType:
        pass

    model.result_set.columns_types[0] = CustomType

    assert model._convert_value(0, "abc") == "abc"


def test_convert_value_invalid_int_fallback(model):
    """
    Verifica fallback en caso de error de conversión.
    """

    model.result_set.columns_types[0] = int

    assert model._convert_value(0, "not_a_number") == "not_a_number"


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
# GENERATE UPDATE QUERIES
# =============================================================================


def test_generate_update_queries(model):
    """
    Verifica que se generan queries UPDATE correctamente.
    """

    model.modified_cells.add((0, 1))  # fila 0 columna name

    queries = model.generate_update_queries()

    assert len(queries) == 1
    assert "UPDATE users" in queries[0]
    assert "name" in queries[0]
    assert "Alice" in queries[0]


# =============================================================================
# GENERATE UPDATE QUERIES (EDGE CASES)
# =============================================================================


def test_generate_update_queries_multiple_rows(model):
    """
    Verifica generación de múltiples queries.
    """

    # fila 0 y 1 modificadas
    model.modified_cells = {(0, 1), (1, 1)}

    queries = model.generate_update_queries()

    assert len(queries) == 2


def test_generate_update_queries_multiple_columns_same_row(model):
    """
    Verifica múltiples columnas en la misma fila.
    """

    model.modified_cells = {(0, 0), (0, 1)}

    queries = model.generate_update_queries()

    assert len(queries) == 1
    assert "SET" in queries[0]
    assert "WHERE" in queries[0]


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
# FORMAT SQL VALUE
# =============================================================================


def test_format_sql_value_string_escape(model):
    """
    Verifica escape de comillas en strings.
    """

    assert model._format_sql_value("O'Reilly") == "'O''Reilly'"


def test_format_sql_value_none(model):
    """
    Verifica que None se convierte en NULL.
    """

    assert model._format_sql_value(None) == "NULL"


def test_format_sql_value_bool(model):
    """
    Verifica conversión de booleanos a SQL.
    """

    assert model._format_sql_value(True) == "TRUE"
    assert model._format_sql_value(False) == "FALSE"


def test_format_sql_value_decimal_and_number(model):
    """
    Verifica Decimal y números.
    """

    assert model._format_sql_value(Decimal("10.5")) == "10.5"
    assert model._format_sql_value(123) == "123"


def test_format_sql_value_date_and_datetime():
    """
    Verifica que date y datetime se formatean correctamente a SQL.
    """

    from datetime import (
        date,
        datetime,
    )

    from ui.widgets.workspace.results_view.result_table_model import ResultTableModel

    model = ResultTableModel.__new__(ResultTableModel)

    result_date = model._format_sql_value(date(2024, 1, 1))
    assert result_date == "'2024-01-01'"

    result_datetime = model._format_sql_value(datetime(2024, 1, 1, 10, 30, 0))

    assert result_datetime == "'2024-01-01T10:30:00'"

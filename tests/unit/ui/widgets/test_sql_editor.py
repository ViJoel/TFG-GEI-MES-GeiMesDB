import pytest
from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QKeyEvent, QTextCursor

from entities.sql_scope import SqlScope
from ui.widgets.workspace.sql_editor.sql_editor import SqlEditor

# =============================================================================
# FIXTURE
# =============================================================================


@pytest.fixture
def editor(qtbot):
    """
    Crea una instancia del SqlEditor para tests UI.
    """

    widget = SqlEditor()
    qtbot.addWidget(widget)
    widget.show()
    return widget


# =============================================================================
# KEY EVENTS
# =============================================================================


def test_tab_inserts_spaces(editor):
    """
    Verifica que TAB inserta 4 espacios.
    """

    event = QKeyEvent(
        QEvent.Type.KeyPress,
        Qt.Key.Key_Tab,
        Qt.KeyboardModifier.NoModifier,
    )

    editor.keyPressEvent(event)

    assert editor.toPlainText() == "    "


def test_ctrl_enter_emits_selected_scope(editor, qtbot):
    """
    Verifica ejecución de texto seleccionado (SELECTED_TEXT).
    """

    editor.setPlainText("SELECT 1;")

    cursor = editor.textCursor()
    cursor.select(QTextCursor.SelectionType.Document)
    editor.setTextCursor(cursor)

    with qtbot.waitSignal(editor.execute_requested) as blocker:
        qtbot.keyPress(
            editor,
            Qt.Key_Return,
            modifier=Qt.ControlModifier,
        )

    statements, scope = blocker.args

    assert scope == SqlScope.SELECTED_TEXT
    assert statements == ["SELECT 1;"]


def test_ctrl_shift_enter_emits_full_script(editor, qtbot):
    """
    Verifica ejecución de script completo (FULL_SCRIPT).
    """

    editor.setPlainText("SELECT 1;\nSELECT 2;")

    with qtbot.waitSignal(editor.execute_requested) as blocker:
        qtbot.keyPress(
            editor,
            Qt.Key_Return,
            modifier=Qt.ControlModifier | Qt.ShiftModifier,
        )

    statements, scope = blocker.args

    assert scope == SqlScope.FULL_SCRIPT
    assert "SELECT 1;" in statements
    assert "SELECT 2;" in statements


# =============================================================================
# SQL PROCESSING
# =============================================================================


def test_split_sql_statements(editor):
    """
    Verifica que el SQL se divide correctamente en sentencias.
    """

    sql = "SELECT 1;\n\nSELECT 2;\n"

    result = editor._split_sql_statements(sql)

    assert result == ["SELECT 1;", "SELECT 2;"]


def test_normalize_sql(editor):
    """
    Verifica normalización de saltos de línea especiales de Qt.
    """

    raw = "SELECT 1\u2029SELECT 2\r\nSELECT 3\rSELECT 4"

    normalized = editor._normalize_sql(raw)

    assert "\u2029" not in normalized
    assert "\r" not in normalized


def test_has_content(editor):
    """
    Verifica detección de contenido útil en texto.
    """

    assert editor._has_content("SELECT 1") is True
    assert editor._has_content("   ") is False
    assert editor._has_content("") is False


def test_get_sql_full_script(editor):
    """
    Verifica obtención de SQL en modo FULL_SCRIPT.
    """

    editor.setPlainText("SELECT 1;")

    result = editor._get_sql(SqlScope.FULL_SCRIPT)

    assert result == "SELECT 1;"


def test_get_sql_empty_returns_none(editor):
    """
    Verifica que texto vacío devuelve None.
    """

    editor.setPlainText("   ")

    result = editor._get_sql(SqlScope.FULL_SCRIPT)

    assert result is None


def test_get_sql_invalid_scope(editor):
    """
    Verifica que _get_sql devuelve None cuando el scope es inválido.
    """

    class FakeScope:
        pass

    result = editor._get_sql(FakeScope())

    assert result is None


# =============================================================================
# SIGNALS
# =============================================================================


def test_execute_signal_emits_correct_data(editor, qtbot):
    """
    Verifica que el signal execute_requested emite datos correctos.
    """

    editor.setPlainText("SELECT 1; SELECT 2;")

    with qtbot.waitSignal(editor.execute_requested) as blocker:
        editor.execute(SqlScope.FULL_SCRIPT)

    statements, scope = blocker.args

    assert isinstance(statements, list)
    assert scope == SqlScope.FULL_SCRIPT


# =============================================================================
# LINE NUMBER AREA
# =============================================================================


def test_line_number_area_exists(editor):
    """
    Verifica que el área de números de línea está creada.
    """

    assert editor.line_number_area is not None


def test_line_number_area_width(editor):
    """
    Verifica que el cálculo del ancho del área de líneas es válido.
    """

    width = editor.line_number_area_width()

    assert isinstance(width, int)
    assert width > 0

from unittest.mock import (
    MagicMock,
    patch,
)

import pytest
from PySide6.QtCore import (
    QEvent,
    QRect,
    Qt,
)
from PySide6.QtGui import (
    QKeyEvent,
    QTextCursor,
)
from PySide6.QtWidgets import QPlainTextEdit

from entities.file import File
from entities.sql_scope import SqlScope
from ui.themes.theme_manager import ThemeManager
from ui.widgets.workspace.sql_editor.sql_editor import SqlEditor

# =============================================================================
# FIXTURE
# =============================================================================


@pytest.fixture
def editor(
    qtbot,
):
    """
    Crea una instancia del SqlEditor para tests UI.
    """

    file = File()

    widget = SqlEditor(file)

    qtbot.addWidget(widget)
    widget.show()

    return widget


# =============================================================================
# INIT
# =============================================================================


def test_editor_saves_file_reference(
    editor,
):
    """
    Verifica que el editor conserva la referencia
    al archivo asociado.
    """

    file = File()

    editor = SqlEditor(file=file)

    assert editor.file is file


def test_editor_content_at_start(
    editor,
):
    """
    Verifica que el contenido inicial del editor
    coincide con el contenido del archivo asociado.
    """
    assert editor.toPlainText() == editor.file.content


# =============================================================================
# KEY EVENTS
# =============================================================================


def test_tab_inserts_spaces(
    editor,
):
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


def test_ctrl_enter_emits_actual_query_scope(
    editor,
    qtbot,
):
    """
    Verifica ejecución de la consulta actual (ACTUAL_QUERY).
    """

    editor.setPlainText("SELECT 1;")

    with qtbot.waitSignal(editor.execute_requested) as blocker:
        qtbot.keyPress(
            editor,
            Qt.Key_Return,
            modifier=Qt.ControlModifier,
        )

    statements, scope = blocker.args

    assert scope == SqlScope.ACTUAL_QUERY
    assert statements == ["SELECT 1"]


def test_ctrl_alt_enter_emits_selected_scope(
    editor,
    qtbot,
):
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
            modifier=Qt.ControlModifier | Qt.AltModifier,
        )

    statements, scope = blocker.args

    assert scope == SqlScope.SELECTED_TEXT
    assert statements == ["SELECT 1"]


def test_ctrl_shift_enter_emits_full_script(
    editor,
    qtbot,
):
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
    assert "SELECT 1" in statements
    assert "SELECT 2" in statements


def test_key_press_event_returns_when_popup_handles_event(
    editor,
):
    """
    Verifica que keyPressEvent finaliza cuando el popup
    del autocompletador consume el evento.
    """

    event = MagicMock(spec=QKeyEvent)

    editor._handle_completer_popup_key_event = MagicMock(return_value=True)

    with patch.object(QPlainTextEdit, "keyPressEvent") as super_key_press:
        editor.keyPressEvent(event)

    super_key_press.assert_not_called()


def test_key_press_event_backtab_does_nothing(
    editor,
):
    """
    Verifica que Shift+Tab se consume y no se delega
    al comportamiento por defecto de Qt.
    """

    event = QKeyEvent(
        QEvent.Type.KeyPress,
        Qt.Key.Key_Backtab,
        Qt.KeyboardModifier.ShiftModifier,
    )

    with patch.object(QPlainTextEdit, "keyPressEvent") as super_key_press:
        editor.keyPressEvent(event)

    super_key_press.assert_not_called()


# =============================================================================
# SQL PROCESSING
# =============================================================================


def test_split_sql_statements(
    editor,
):
    """
    Verifica que el SQL se divide correctamente en sentencias.
    """

    sql = "SELECT 1;\n\nSELECT 2;\n"

    result = editor._split_sql_statements(sql)

    assert result == ["SELECT 1", "SELECT 2"]


def test_normalize_sql(
    editor,
):
    """
    Verifica normalización de saltos de línea especiales de Qt.
    """

    raw = "SELECT 1\u2029SELECT 2\r\nSELECT 3\rSELECT 4"

    normalized = editor._normalize_sql(raw)

    assert "\u2029" not in normalized
    assert "\r" not in normalized


def test_has_content(
    editor,
):
    """
    Verifica detección de contenido útil en texto.
    """

    assert editor._has_content("SELECT 1") is True
    assert editor._has_content("   ") is False
    assert editor._has_content("") is False


def test_get_sql_full_script(
    editor,
):
    """
    Verifica obtención de SQL en modo FULL_SCRIPT.
    """

    editor.setPlainText("SELECT 1;")

    result = editor._get_sql(SqlScope.FULL_SCRIPT)

    assert result == "SELECT 1;"


def test_get_sql_empty_returns_none(
    editor,
):
    """
    Verifica que texto vacío devuelve None.
    """

    editor.setPlainText("   ")

    result = editor._get_sql(SqlScope.FULL_SCRIPT)

    assert result is None


def test_get_sql_invalid_scope(
    editor,
):
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


def test_execute_signal_emits_correct_data(
    editor,
    qtbot,
):
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
# EXECUTE
# =============================================================================


def test_execute_does_not_emit_signal_when_sql_is_none(
    editor,
    qtbot,
):
    """
    Verifica que no se emite la señal de ejecución
    cuando no existe SQL válido.
    """

    editor.setPlainText("")

    with qtbot.assertNotEmitted(editor.execute_requested):
        editor.execute(SqlScope.FULL_SCRIPT)


# =============================================================================
# LINE NUMBER AREA
# =============================================================================


def test_line_number_area_exists(
    editor,
):
    """
    Verifica que el área de números de línea está creada.
    """

    assert editor.line_number_area is not None


def test_line_number_area_width(
    editor,
):
    """
    Verifica que el cálculo del ancho del área de líneas es válido.
    """

    width = editor.line_number_area_width()

    assert isinstance(width, int)
    assert width > 0


def test_update_line_number_area_scrolls_when_dy_is_not_zero(
    editor,
):
    """
    Verifica que el área de números se desplaza cuando
    existe un desplazamiento vertical.
    """

    editor.line_number_area.scroll = MagicMock()
    editor._update_line_number_area_width = MagicMock()

    rect = QRect(0, 0, 100, 100)

    editor._update_line_number_area(
        rect,
        10,
    )

    editor.line_number_area.scroll.assert_called_once_with(
        0,
        10,
    )


# =============================================================================
# INSERT QUERY AT CURSOR
# =============================================================================


def test_insert_query_at_cursor_inserts_text(
    editor,
):
    """
    Verifica que el texto SQL se inserta en la posición
    actual del cursor.
    """

    editor.setPlainText("SELECT ")

    cursor = editor.textCursor()
    cursor.movePosition(cursor.MoveOperation.End)
    editor.setTextCursor(cursor)

    editor.insert_query_at_cursor("* FROM users")

    assert editor.toPlainText() == "SELECT * FROM users"


def test_insert_query_at_cursor_ignores_empty_text(
    editor,
):
    """
    Verifica que no se modifica el contenido cuando
    el texto a insertar está vacío.
    """

    editor.setPlainText("SELECT *")

    editor.insert_query_at_cursor("")

    assert editor.toPlainText() == "SELECT *"


# =============================================================================
# CURRENT QUERY
# =============================================================================


def test_get_current_query_returns_first_statement(
    editor,
):
    """
    Verifica que devuelve la sentencia donde está
    situado el cursor.
    """

    editor.setPlainText("SELECT 1;\n" "SELECT 2;")

    cursor = editor.textCursor()
    cursor.setPosition(3)
    editor.setTextCursor(cursor)

    result = editor._get_current_query()

    assert result == "SELECT 1;"


def test_get_current_query_returns_second_statement(
    editor,
):
    """
    Verifica que detecta correctamente una sentencia
    posterior dentro del documento.
    """

    editor.setPlainText("SELECT 1;\n" "SELECT 2;")

    cursor = editor.textCursor()
    cursor.setPosition(editor.toPlainText().find("SELECT 2") + 3)
    editor.setTextCursor(cursor)

    result = editor._get_current_query()

    assert result == "SELECT 2;"


def test_get_current_query_returns_none_between_statements(
    editor,
):
    """
    Verifica que no devuelve una consulta cuando
    el cursor está fuera de cualquier sentencia.
    """

    editor.setPlainText("SELECT 1;\n\n\nSELECT 2;")

    cursor = editor.textCursor()
    cursor.setPosition(editor.toPlainText().find("\n\n\n") + 1)
    editor.setTextCursor(cursor)

    result = editor._get_current_query()

    assert result is None


def test_get_current_query_empty_editor_returns_none(
    editor,
):
    """
    Verifica que no devuelve consulta si el editor está vacío.
    """

    editor.setPlainText("")

    result = editor._get_current_query()

    assert result is None


def test_get_current_query_ignores_statement_not_found(
    editor,
):
    """
    Verifica que devuelve None cuando la sentencia
    obtenida no existe dentro del documento.
    """

    editor.setPlainText("SELECT 1;")

    fake_statement = "SELECT 2;"

    with patch(
        "ui.widgets.workspace.sql_editor.sql_editor.sqlparse.parse",
        return_value=[fake_statement],
    ):
        result = editor._get_current_query()

    assert result is None


# =============================================================================
# DOCUMENT COMPLETION
# =============================================================================


def test_on_text_changed_updates_document_completion(
    editor,
):
    """
    Verifica que el editor delega la actualización del
    autocompletado dinámico al completer cuando cambia
    el contenido del documento.
    """

    editor.completer.update_document_completion = MagicMock()

    text = "SELECT :id"

    editor.setPlainText(text)

    editor.completer.update_document_completion.assert_called_once_with(
        sql=text,
    )


def test_on_text_changed_passes_current_document_text(
    editor,
):
    """
    Verifica que siempre se envía al completer el contenido
    completo y actualizado del documento.
    """

    editor.completer.update_document_completion = MagicMock()

    text = "SELECT @var FROM table"

    editor.setPlainText(text)

    editor.completer.update_document_completion.assert_called_once_with(
        sql=text,
    )


def test_update_completer_does_not_show_popup_on_backspace_if_hidden(
    editor,
):
    """
    Verifica que pulsar Backspace no abre el popup cuando
    éste no estaba visible.
    """

    editor.completer.complete_at = MagicMock()
    editor.completer.popup().hide()

    event = QKeyEvent(
        QEvent.Type.KeyPress,
        Qt.Key.Key_Backspace,
        Qt.KeyboardModifier.NoModifier,
    )

    editor._update_completer(event)

    editor.completer.complete_at.assert_not_called()


def test_update_completer_keeps_popup_updated_on_backspace_if_visible(
    editor,
):
    """
    Verifica que si el popup ya estaba visible, Backspace
    vuelve a actualizar el autocompletador.
    """

    editor.completer.popup = MagicMock()
    editor.completer.popup.return_value.isVisible.return_value = True

    editor.completer.complete_at = MagicMock()

    editor.text_under_cursor = MagicMock(return_value="SE")
    editor.cursorRect = MagicMock(return_value=QRect())

    event = MagicMock(spec=QKeyEvent)
    event.key.return_value = Qt.Key.Key_Backspace
    event.modifiers.return_value = Qt.KeyboardModifier.NoModifier
    event.text.return_value = "x"

    editor._update_completer(event)

    editor.completer.complete_at.assert_called_once_with(
        prefix="SE",
        rect=editor.cursorRect.return_value,
    )


def test_handle_completer_popup_key_event_returns_false_for_return(
    editor,
):
    """
    Verifica que Return no es gestionado por el popup
    para permitir insertar una nueva línea.
    """

    editor.completer.popup().isVisible = MagicMock(return_value=True)

    event = MagicMock(spec=QKeyEvent)
    event.key.return_value = Qt.Key.Key_Return

    assert editor._handle_completer_popup_key_event(event) is False


def test_handle_completer_popup_key_event_returns_true_for_tab(
    editor,
):
    """
    Verifica que Tab es gestionado por el popup
    cuando éste está visible.
    """

    editor.completer.popup().isVisible = MagicMock(return_value=True)

    event = MagicMock(spec=QKeyEvent)
    event.key.return_value = Qt.Key.Key_Tab

    assert editor._handle_completer_popup_key_event(event) is True


def test_text_under_cursor_returns_empty_when_cursor_after_separator(
    editor,
):
    """
    Verifica que no se retrocede cuando el carácter
    anterior no forma parte de una palabra SQL.
    """

    editor.setPlainText("SELECT ")

    cursor = editor.textCursor()
    cursor.movePosition(QTextCursor.MoveOperation.End)
    editor.setTextCursor(cursor)

    assert editor.text_under_cursor() == ""


# =============================================================================
# FILES
# =============================================================================


def test_text_changed_updates_file_content(
    editor,
):
    """
    Verifica que modificar el contenido del editor
    actualiza el contenido del archivo asociado.
    """

    editor.setPlainText("SELECT * FROM users")

    assert editor.file.content == "SELECT * FROM users"


def test_text_changed_emits_file_modified(
    editor,
    qtbot,
):
    """
    Verifica que modificar el contenido del editor
    emite la señal file_modified.
    """

    with qtbot.waitSignal(editor.file_modified) as blocker:
        editor.setPlainText("SELECT 1")

    assert blocker.args == [editor.file]


def test_ctrl_s_emits_save_changes(
    editor,
    qtbot,
):
    """
    Verifica que Ctrl+S emite la señal
    save_changes con el archivo actual.
    """

    with qtbot.waitSignal(editor.save_changes) as blocker:
        qtbot.keyPress(
            editor,
            Qt.Key_S,
            modifier=Qt.ControlModifier,
        )

    assert blocker.args == [editor.file]


def test_ctrl_r_emits_rename_file(
    editor,
    qtbot,
):
    """
    Verifica que Ctrl+R emite la señal
    rename_file con el archivo actual.
    """

    with qtbot.waitSignal(editor.rename_file) as blocker:
        qtbot.keyPress(
            editor,
            Qt.Key_R,
            modifier=Qt.ControlModifier,
        )

    assert blocker.args == [editor.file]


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("SELECT customer_id", "customer_id"),
        ("SELECT * FROM users WHERE id = :user_id", ":user_id"),
        ("SELECT @my_var", "@my_var"),
    ],
)
def test_text_under_cursor_returns_word(
    editor,
    text,
    expected,
):
    editor.setPlainText(text)

    cursor = editor.textCursor()
    cursor.movePosition(QTextCursor.MoveOperation.End)
    editor.setTextCursor(cursor)

    assert editor.text_under_cursor() == expected


# =============================================================================
# FORCE UPDATE COMPLETER
# =============================================================================


def test_force_update_completer_forces_document_completion_refresh(
    editor,
):
    """
    Verifica que force_update_completer solicita una
    actualización forzada del autocompletador.
    """

    editor.completer.update_document_completion = MagicMock()

    editor.force_update_completer()

    editor.completer.update_document_completion.assert_called_once_with(
        force_update=True,
        schema_data=None,
    )


# =============================================================================
# THEME
# =============================================================================


def test_connect_signals_connects_theme_changed(editor):
    """
    Verifica que el editor se conecta a la señal
    theme_changed del ThemeManager.
    """

    with patch(
        "ui.widgets.workspace.sql_editor.sql_editor.ThemeManager.events"
    ) as events:

        signal = MagicMock()
        events.return_value.theme_changed = signal

        editor._connect_signals()

        signal.connect.assert_any_call(
            editor._on_theme_changed,
        )


def test_on_theme_changed_refreshes_theme_dependent_components(
    editor,
):
    """
    Verifica que al cambiar el tema se actualizan
    todos los componentes dependientes del mismo.
    """

    editor._highlight_current_line = MagicMock()
    editor.force_update_completer = MagicMock()
    editor.syntax_highlighter.reload_theme = MagicMock()
    editor.line_number_area.update = MagicMock()
    editor.viewport().update = MagicMock()

    editor._on_theme_changed("dark")

    editor._highlight_current_line.assert_called_once_with()

    editor.force_update_completer.assert_called_once_with()

    editor.syntax_highlighter.reload_theme.assert_called_once_with()

    editor.line_number_area.update.assert_called_once_with()

    editor.viewport().update.assert_called_once_with()


def test_theme_changed_signal_updates_editor(editor):
    """
    Verifica que emitir theme_changed ejecuta el
    refresco del editor.
    """

    editor._on_theme_changed = MagicMock()

    ThemeManager.events().theme_changed.disconnect()

    ThemeManager.events().theme_changed.connect(
        editor._on_theme_changed,
    )

    ThemeManager.events().theme_changed.emit("dark")

    editor._on_theme_changed.assert_called_once_with("dark")


# =============================================================================
# TEMPLATE
# =============================================================================


def test_set_template_loads_default_sql(
    editor,
):
    """
    Verifica que set_template carga el SQL
    definido como plantilla por defecto.
    """

    editor.setPlainText("SELECT 1;")

    editor.set_template()

    assert editor.toPlainText() == editor.DEFAULT_SQL


def test_set_template_moves_cursor_to_end(
    editor,
):
    """
    Verifica que set_template sitúa el cursor
    al final del contenido de la plantilla.
    """

    editor.set_template()

    cursor = editor.textCursor()

    assert cursor.position() == len(editor.DEFAULT_SQL)
    assert cursor.position() == cursor.document().characterCount() - 1

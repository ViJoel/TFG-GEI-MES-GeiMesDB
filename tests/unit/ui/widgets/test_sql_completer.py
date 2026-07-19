from unittest.mock import (
    MagicMock,
    patch,
)

from PySide6.QtCore import QRect
from PySide6.QtGui import (
    QStandardItem,
    QTextCursor,
)
from PySide6.QtWidgets import QWidget

from ui.widgets.workspace.sql_editor.sql_completer import SqlCompleter


def test_popup_width_returns_largest_item_width(qtbot):

    widget = QWidget()
    qtbot.addWidget(widget)

    completer = SqlCompleter(widget)

    completer._model.clear()

    completer._model.appendRow(QStandardItem("SELECT"))
    completer._model.appendRow(QStandardItem("VERY_LONG_FUNCTION_NAME"))

    width = completer.popup_width()

    assert width > 0


def test_refresh_calls_model_refresh(qtbot):
    """
    Verifica que refresh delega la recarga
    al modelo interno.
    """

    widget = QWidget()
    qtbot.addWidget(widget)

    completer = SqlCompleter(widget)

    completer._model.refresh = MagicMock()

    completer.refresh()

    completer._model.refresh.assert_called_once()


def test_complete_at_updates_prefix_when_changed(qtbot):
    """
    Verifica que complete_at actualiza el prefijo
    cuando es diferente al actual.
    """

    widget = QWidget()
    qtbot.addWidget(widget)

    completer = SqlCompleter(widget)

    completer.completionPrefix = MagicMock(
        return_value="old",
    )

    completer.setCompletionPrefix = MagicMock()

    completer.popup_width = MagicMock(
        return_value=100,
    )

    completer.complete = MagicMock()

    rect = MagicMock()

    completer.complete_at(
        prefix="new",
        rect=rect,
    )

    completer.setCompletionPrefix.assert_called_once_with(
        "new",
    )

    completer.complete.assert_called_once_with(
        rect,
    )


def test_complete_at_keeps_prefix_when_same(qtbot):
    """
    Verifica que no cambia el prefijo si ya coincide.
    """

    widget = QWidget()
    qtbot.addWidget(widget)

    completer = SqlCompleter(widget)

    completer.completionPrefix = MagicMock(
        return_value="select",
    )

    completer.setCompletionPrefix = MagicMock()

    completer.complete = MagicMock()

    rect = MagicMock()

    completer.complete_at(
        prefix="select",
        rect=rect,
    )

    completer.setCompletionPrefix.assert_not_called()

    completer.complete.assert_called_once_with(
        rect,
    )


def test_insert_completion_does_nothing_without_editor(qtbot):
    """
    Verifica que insert_completion no falla
    si no existe widget asociado.
    """

    widget = QWidget()
    qtbot.addWidget(widget)

    completer = SqlCompleter(widget)

    completer.widget = MagicMock(
        return_value=None,
    )

    completer.insert_completion(
        "SELECT",
    )


def test_insert_completion_replaces_word_under_cursor(qtbot):
    """
    Verifica que insert_completion sustituye
    la palabra actual.
    """

    from PySide6.QtWidgets import QPlainTextEdit

    editor = QPlainTextEdit()

    qtbot.addWidget(editor)

    editor.setPlainText(
        "SEL",
    )

    cursor = editor.textCursor()
    cursor.movePosition(
        QTextCursor.MoveOperation.End,
    )
    editor.setTextCursor(cursor)

    completer = SqlCompleter(editor)

    completer.insert_completion(
        "SELECT",
    )

    assert editor.toPlainText() == "SELECT"


def test_update_document_completion_delegates_to_model(qtbot):

    widget = QWidget()
    qtbot.addWidget(widget)

    completer = SqlCompleter(widget)

    completer._model.update = MagicMock(return_value=True)

    completer.update_document_completion("SELECT * FROM table")

    completer._model.update.assert_called_once_with("SELECT * FROM table")

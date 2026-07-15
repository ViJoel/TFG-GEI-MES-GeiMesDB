from datetime import datetime

from PySide6.QtCore import (
    QEvent,
    QPointF,
    Qt,
)
from PySide6.QtGui import QMouseEvent

from entities.queries_history_entry import QueriesHistoryEntry
from ui.widgets.workspace.results_view.session_queries_history_item import (
    SessionQueriesHistoryItem,
)

# =============================================================================
# FIXTURES
# =============================================================================


def create_entry(query="SELECT * FROM users"):
    return QueriesHistoryEntry(
        query=query,
        executed_at=datetime(2025, 1, 1, 12, 0, 0),
    )


# =============================================================================
# TESTS
# =============================================================================


def test_widget_builds_labels(qtbot):
    widget = SessionQueriesHistoryItem(create_entry())
    qtbot.addWidget(widget)

    assert widget.layout().count() == 2


def test_mouse_double_click_emits_signal(qtbot):
    entry = create_entry("SELECT 123")

    widget = SessionQueriesHistoryItem(entry)
    qtbot.addWidget(widget)

    received = []

    widget.query_double_clicked.connect(received.append)

    event = QMouseEvent(
        QEvent.Type.MouseButtonDblClick,
        QPointF(1, 1),
        QPointF(1, 1),
        QPointF(1, 1),
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )

    widget.mouseDoubleClickEvent(event)

    assert received == ["SELECT 123"]


def test_format_query_preview_normal(qtbot):
    widget = SessionQueriesHistoryItem(create_entry())
    qtbot.addWidget(widget)

    assert widget._format_query_preview("SELECT 1") == "SELECT 1"


def test_format_query_preview_truncates_long_line(qtbot):
    widget = SessionQueriesHistoryItem(create_entry())
    qtbot.addWidget(widget)

    preview = widget._format_query_preview(
        "A" * 20,
        max_line_length=10,
    )

    assert preview == "AAAAAAA..."


def test_format_query_preview_truncates_number_of_lines(qtbot):
    widget = SessionQueriesHistoryItem(create_entry())
    qtbot.addWidget(widget)

    query = "\n".join(f"line {i}" for i in range(10))

    preview = widget._format_query_preview(
        query,
        max_lines=3,
    )

    assert preview == ("line 0\n" "line 1\n" "line 2\n" "...")

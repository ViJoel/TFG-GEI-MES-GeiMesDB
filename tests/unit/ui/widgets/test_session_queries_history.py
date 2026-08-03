from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtGui import QFocusEvent

from entities.queries_history_entry import QueriesHistoryEntry
from ui.widgets.workspace.results_view.session_queries_history import (
    SessionQueriesHistory,
)

# =============================================================================
# FIXTURES
# =============================================================================


def create_entry(query="SELECT * FROM users"):
    """
    Crea una entrada válida para las pruebas.
    """

    return QueriesHistoryEntry(
        query=query,
        executed_at=datetime(2025, 1, 1, 12, 0, 0),
    )


# =============================================================================
# INIT
# =============================================================================


def test_widget_starts_empty(qtbot):
    """
    El historial debe comenzar vacío.
    """

    widget = SessionQueriesHistory()
    qtbot.addWidget(widget)

    assert widget.count() == 0


# =============================================================================
# ADD ENTRY
# =============================================================================


def test_add_entry_appends_item(qtbot):
    """
    add_entry debe añadir un elemento al final.
    """

    widget = SessionQueriesHistory()
    qtbot.addWidget(widget)

    entry = create_entry()

    widget.add_entry(entry)

    assert widget.count() == 1

    item = widget.item(0)

    assert item.data(Qt.ItemDataRole.UserRole) is entry


def test_add_entry_inserts_item_at_row(qtbot):
    """
    Debe insertar en la posición indicada.
    """

    widget = SessionQueriesHistory()
    qtbot.addWidget(widget)

    first = create_entry("SELECT 1")
    second = create_entry("SELECT 2")

    widget.add_entry(first)
    widget.add_entry(second, row=0)

    assert widget.count() == 2

    assert widget.item(0).data(Qt.ItemDataRole.UserRole).query == "SELECT 2"

    assert widget.item(1).data(Qt.ItemDataRole.UserRole).query == "SELECT 1"


# =============================================================================
# FOCUS
# =============================================================================


def test_focus_out_calls_clear_selection(qtbot, monkeypatch):
    widget = SessionQueriesHistory()
    qtbot.addWidget(widget)

    called = False

    def fake():
        nonlocal called
        called = True

    monkeypatch.setattr(widget, "clearSelection", fake)

    widget.focusOutEvent(QFocusEvent(QFocusEvent.Type.FocusOut))

    assert called


# =============================================================================
# SIGNALS
# =============================================================================


def test_double_click_emits_query_selected(qtbot):
    """
    El doble clic sobre un elemento debe propagar
    la consulta SQL.
    """

    widget = SessionQueriesHistory()
    qtbot.addWidget(widget)

    entry = create_entry("SELECT 123")

    widget.add_entry(entry)

    item = widget.itemWidget(widget.item(0))

    received = []

    widget.query_selected.connect(received.append)

    item.query_double_clicked.emit(entry.query)

    assert received == ["SELECT 123"]


# =============================================================================
# INTERNAL DATA
# =============================================================================


def test_item_stores_original_entry(qtbot):
    """
    Cada QListWidgetItem debe conservar la entrada
    original en UserRole.
    """

    widget = SessionQueriesHistory()
    qtbot.addWidget(widget)

    entry = create_entry()

    widget.add_entry(entry)

    stored = widget.item(0).data(Qt.ItemDataRole.UserRole)

    assert stored is entry


def test_item_has_embedded_widget(qtbot):
    """
    Cada elemento debe tener asociado un
    SessionQueriesHistoryItem.
    """

    widget = SessionQueriesHistory()
    qtbot.addWidget(widget)

    widget.add_entry(create_entry())

    assert widget.itemWidget(widget.item(0)) is not None


# =============================================================================
# focusOutEvent
# =============================================================================


def test_focus_out_event_clears_selection(qtbot, monkeypatch):
    """
    Al perder el foco debe limpiarse la selección.
    """

    widget = SessionQueriesHistory()
    qtbot.addWidget(widget)

    called = False

    def fake_clear():
        nonlocal called
        called = True

    monkeypatch.setattr(widget, "clearSelection", fake_clear)

    event = QFocusEvent(QFocusEvent.Type.FocusOut)

    widget.focusOutEvent(event)

    assert called


# =============================================================================
# _add_list_item
# =============================================================================


def test_add_list_item_inserts_at_given_row(qtbot):
    """
    Si se indica una fila debe utilizar insertItem.
    """

    widget = SessionQueriesHistory()
    qtbot.addWidget(widget)

    widget.add_entry(create_entry())
    widget.add_entry(create_entry(), row=0)

    assert widget.count() == 2

    item = widget.item(0)

    assert item.data(Qt.ItemDataRole.UserRole).query == "SELECT * FROM users"


def test_add_list_item_appends_when_row_is_none(qtbot):
    """
    Si no se indica fila debe añadirse al final.
    """

    widget = SessionQueriesHistory()
    qtbot.addWidget(widget)

    first = QueriesHistoryEntry(
        query="SELECT 1",
        executed_at=datetime.now(),
    )

    second = QueriesHistoryEntry(
        query="SELECT 2",
        executed_at=datetime.now(),
    )

    widget.add_entry(first)
    widget.add_entry(second)

    assert widget.count() == 2

    assert widget.item(0).data(Qt.ItemDataRole.UserRole).query == "SELECT 1"

    assert widget.item(1).data(Qt.ItemDataRole.UserRole).query == "SELECT 2"

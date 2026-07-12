from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtGui import QFocusEvent

from PySide6.QtCore import (
    Qt,
    Signal,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QListWidget,
    QListWidgetItem,
)

from entities.queries_history_entry import QueriesHistoryEntry
from ui.widgets.workspace.results_view.session_queries_history_item import (
    SessionQueriesHistoryItem,
)


class SessionQueriesHistory(QListWidget):

    # =================
    # === VARIABLES ===
    # =================

    query_selected = Signal(str)

    # ============
    # === INIT ===
    # ============

    def __init__(
        self,
    ) -> None:

        super().__init__()

        self.setObjectName("session_queries_history")

        self._setup_ui()

    # ================
    # === UI SETUP ===
    # ================

    def _setup_ui(
        self,
    ) -> None:
        """
        Construye la interfaz principal del widget.
        """

        self.setSpacing(4)

        self.setVerticalScrollMode(
            QAbstractItemView.ScrollMode.ScrollPerPixel,
        )
        self.verticalScrollBar().setSingleStep(10)

        self.setHorizontalScrollMode(
            QAbstractItemView.ScrollMode.ScrollPerPixel,
        )
        self.horizontalScrollBar().setSingleStep(10)

        # Elimina el foco de teclado
        # Usado para eliminar el rectángulo
        # de selección que viene por defecto.
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    # ==================
    # === UI HELPERS ===
    # ==================

    def _add_list_item(self, entry: QueriesHistoryEntry, row: int = None):

        item = QListWidgetItem()

        item.setData(
            Qt.ItemDataRole.UserRole,
            entry,
        )

        widget = SessionQueriesHistoryItem(entry)

        item.setSizeHint(widget.sizeHint())

        widget.query_double_clicked.connect(self.query_selected.emit)

        # Si especificamos una fila (como la 0), lo insertamos ahí.
        # Si no, va al final por defecto.
        if row is not None:
            self.insertItem(row, item)
        else:
            self.addItem(item)

        self.setItemWidget(
            item,
            widget,
        )

    # ====================
    # === QT OVERRIDES ===
    # ====================

    def focusOutEvent(
        self,
        event: QFocusEvent,
    ) -> None:
        """
        Limpia la selección cuando la vista pierde el foco.
        """

        self.clearSelection()

        super().focusOutEvent(event)

    # ==================
    # === PUBLIC API ===
    # ==================

    def add_entry(
        self,
        entry: QueriesHistoryEntry,
        row: int | None = None,
    ) -> None:
        """
        Añade una nueva entrada al historial
        de consultas de la sesión.

        Args:
            entry (QueriesHistoryEntry):
                Nueva entrada que se añadirá al historial.

            row (int | None):
                Posición donde insertar la entrada.

                - Si se especifica, la entrada se inserta
                en dicha posición.
                - Si es `None`, la entrada se añade al
                final del historial.
        """

        self._add_list_item(
            entry,
            row,
        )

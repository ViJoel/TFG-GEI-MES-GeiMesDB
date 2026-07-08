from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtGui import QMouseEvent

from PySide6.QtCore import (
    Qt,
    Signal,
)
from PySide6.QtWidgets import (
    QLabel,
    QWidget,
)

from entities.queries_history_entry import QueriesHistoryEntry
from ui.utils.layouts import vbox


class SessionQueriesHistoryItem(QWidget):

    # =================
    # === VARIABLES ===
    # =================

    query_double_clicked = Signal(str)

    # ============
    # === INIT ===
    # ============

    def __init__(
        self,
        entry: QueriesHistoryEntry,
    ) -> None:

        super().__init__()

        self.entry = entry

        self.setObjectName("session_queries_history_item")

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

        self.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground,
            True,
        )

        layout = vbox(
            ml=4,
            mt=4,
            mr=4,
            mb=4,
            sp=2,
        )
        self.setLayout(layout)

        date = QLabel(
            text=self.entry.executed_at.strftime("%Y/%m/%d\t-\t%H:%M:%S"),
        )
        date.setObjectName("session_queries_history_item_date")

        date.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground,
            True,
        )

        query = QLabel(
            text=self._format_query_preview(self.entry.query),
        )
        query.setObjectName("session_queries_history_item_query")

        query.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground,
            True,
        )

        layout.addWidget(date)
        layout.addWidget(query)

    # ====================
    # === QT OVERRIDES ===
    # ====================

    def mouseDoubleClickEvent(
        self,
        event: QMouseEvent,
    ) -> None:
        """
        Detecta el doble clic sobre el widget y emite
        la consulta SQL hacia el exterior.
        """

        # Emitimos el texto de la query hacia afuera
        self.query_double_clicked.emit(self.entry.query)

        # Aseguramos que Qt siga procesando el evento si es necesario
        super().mouseDoubleClickEvent(event)

    # ===================
    # === PRIVATE API ===
    # ===================

    def _format_query_preview(
        self,
        query: str,
        max_lines: int = 6,
        max_line_length: int = 100,
    ) -> str:
        """
        Genera una vista previa de una consulta SQL.

        - Limita el número de líneas mostradas.
        - Limita la longitud de cada línea.
        - Añade "..." cuando se omite contenido.

        Args:
            query:
                Consulta SQL original.

            max_lines:
                Número máximo de líneas a mostrar.

            max_line_length:
                Longitud máxima de cada línea.

        Returns:
            str:
                Vista previa de la consulta.
        """

        lines = query.splitlines()
        preview: list[str] = []

        for line in lines[:max_lines]:
            line = line.rstrip()

            if len(line) > max_line_length:
                line = line[: max_line_length - 3].rstrip() + "..."

            preview.append(line)

        if len(lines) > max_lines:
            preview.append("...")

        return "\n".join(preview)

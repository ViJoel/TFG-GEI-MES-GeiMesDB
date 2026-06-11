from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QKeyEvent, QPainter, QTextFormat
from PySide6.QtWidgets import QPlainTextEdit, QTextEdit

from ui.widgets.workspace.sql_editor.line_number_area import LineNumberArea
from ui.widgets.workspace.sql_scope import SqlScope


class SqlEditor(QPlainTextEdit):

    # =================
    # === VARIABLES ===
    # =================

    execute_requested = Signal(str, object)

    # ============
    # === INIT ===
    # ============

    def __init__(self):
        """
        Inicializa el editor sql.
        """

        super().__init__()

        self._setup_ui()
        self._connect_signals()

    # ================
    # === UI SETUP ===
    # ================

    def _setup_ui(self) -> None:
        """
        Construye la interfaz principal del widget.
        """

        self.setPlaceholderText("Write SQL query...")

        self.line_number_area = LineNumberArea(self)

        self._update_line_number_area_width()

    # ==================
    # === UI HELPERS ===
    # ==================

    def line_number_area_width(self) -> int:

        digits = len(str(max(1, self.blockCount())))

        return 10 + self.fontMetrics().horizontalAdvance("9") * digits

    def _update_line_number_area_width(self) -> None:

        self.setViewportMargins(
            self.line_number_area_width(),
            0,
            0,
            0,
        )

    def _update_line_number_area(
        self,
        rect,
        dy,
    ) -> None:

        if dy:
            self.line_number_area.scroll(0, dy)

        else:
            self.line_number_area.update(
                0,
                rect.y(),
                self.line_number_area.width(),
                rect.height(),
            )

        if rect.contains(self.viewport().rect()):
            self._update_line_number_area_width()

    def _highlight_current_line(self) -> None:
        """
        Resalta visualmente la línea donde se
        encuentra el cursor.
        """

        selections = []

        if not self.isReadOnly():

            selection = QTextEdit.ExtraSelection()

            selection.format.setBackground(QColor("#2d2d2d"))

            selection.format.setProperty(
                QTextFormat.Property.FullWidthSelection,
                True,
            )

            selection.cursor = self.textCursor()

            # Evitar seleccionar texto
            selection.cursor.clearSelection()

            selections.append(selection)

        self.setExtraSelections(selections)

    # ===============
    # === SIGNALS ===
    # ===============

    def _connect_signals(self) -> None:

        self.blockCountChanged.connect(self._update_line_number_area_width)

        self.updateRequest.connect(self._update_line_number_area)

        self.cursorPositionChanged.connect(self._highlight_current_line)

    # =====================
    # === EVENT HELPERS ===
    # =====================

    def _emit_execute_requested(self, scope: SqlScope) -> None:
        """
        Emite la solicitud de ejecución del SQL
        correspondiente al ámbito especificado.
        """

        sql = self._get_sql(scope)

        if sql is not None:

            self.execute_requested.emit(
                sql,
                scope,
            )

    # ====================
    # === QT OVERRIDES ===
    # ====================

    def keyPressEvent(
        self,
        event: QKeyEvent,
    ) -> None:

        modifiers = event.modifiers()

        # Tab -> 4 espacios
        if event.key() == Qt.Key.Key_Tab:
            self.insertPlainText("    ")
            return

        # Ctrl + Shift + Enter -> Ejecutar script
        elif (
            event.key() == Qt.Key.Key_Return
            and modifiers & Qt.KeyboardModifier.ControlModifier
            and modifiers & Qt.KeyboardModifier.ShiftModifier
        ):
            self._emit_execute_requested(SqlScope.FULL_SCRIPT)
            return

        # Ctrl + Enter -> Ejecutar texto seleccionado
        elif (
            event.key() == Qt.Key.Key_Return
            and modifiers & Qt.KeyboardModifier.ControlModifier
        ):
            self._emit_execute_requested(SqlScope.SELECTED_TEXT)
            return

        super().keyPressEvent(event)

    def resizeEvent(self, event):

        super().resizeEvent(event)

        rect = self.contentsRect()

        self.line_number_area.setGeometry(
            rect.left(),
            rect.top(),
            self.line_number_area_width(),
            rect.height(),
        )

    # ===================
    # === PRIVATE API ===
    # ===================

    def _has_content(
        self,
        text: str,
    ) -> bool:
        """
        Comprueba si el texto contiene caracteres
        distintos de espacios en blanco.
        """

        return bool(text.strip())

    def _get_sql(self, scope: SqlScope) -> str | None:

        if scope == SqlScope.SELECTED_TEXT:
            text = self.textCursor().selectedText()

        elif scope == SqlScope.FULL_SCRIPT:
            text = self.toPlainText()

        else:
            return None

        return self._normalize_sql(text) if self._has_content(text) else None

    def _normalize_sql(self, text: str) -> str:
        """
        Convierte caracteres especiales utilizados por Qt
        en saltos de línea convencionales.
        """

        return text.replace("\u2029", "\n").replace("\r\n", "\n").replace("\r", "\n")

    # ==================
    # === PUBLIC API ===
    # ==================

    def line_number_area_paint_event(self, event) -> None:

        painter = QPainter(self.line_number_area)

        painter.fillRect(
            event.rect(),
            QColor("#1e1e1e"),
        )

        block = self.firstVisibleBlock()

        block_number = block.blockNumber()

        top = round(
            self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        )

        bottom = top + round(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():

            if block.isVisible() and bottom >= event.rect().top():

                number = str(block_number + 1)

                painter.setPen(QColor("#808080"))

                painter.drawText(
                    0,
                    top,
                    self.line_number_area.width() - 5,
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight,
                    number,
                )

            block = block.next()

            top = bottom

            bottom = top + round(self.blockBoundingRect(block).height())

            block_number += 1

import sqlparse
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import (
    QColor,
    QKeyEvent,
    QPainter,
    QPaintEvent,
    QResizeEvent,
    QTextFormat,
)
from PySide6.QtWidgets import QPlainTextEdit, QTextEdit

from ui.themes.theme_manager import ThemeManager
from ui.widgets.workspace.sql_editor.line_number_area import LineNumberArea
from ui.widgets.workspace.sql_editor.sql_scope import SqlScope


class SqlEditor(QPlainTextEdit):
    """
    Widget encargado de proporcionar un editor
    de texto orientado a SQL.

    Responsabilidades:
    - Gestionar la edición del texto SQL.
    - Mostrar numeración de líneas.
    - Resaltar la línea actual.
    - Emitir solicitudes de ejecución.
    - Gestionar atajos de teclado del editor.
    """

    # =================
    # === VARIABLES ===
    # =================

    execute_requested = Signal(
        list,
        object,
    )

    # ============
    # === INIT ===
    # ============

    def __init__(
        self,
    ) -> None:
        """
        Inicializa el editor sql.
        """

        super().__init__()

        self.setObjectName("sql_editor")

        self._setup_ui()
        self._connect_signals()

    # ================
    # === UI SETUP ===
    # ================

    def _setup_ui(
        self,
    ) -> None:
        """
        Construye la interfaz principal del widget.
        """

        self.setPlaceholderText("Write SQL query...")

        self.line_number_area = LineNumberArea(self)

        self._update_line_number_area_width()

    # ==================
    # === UI HELPERS ===
    # ==================

    def line_number_area_width(
        self,
    ) -> int:
        """
        Calcula el ancho necesario para mostrar
        correctamente los números de línea.

        Returns:
            int:
                Ancho requerido para el área
                lateral de numeración.
        """

        digits = len(str(max(1, self.blockCount())))

        return 10 + self.fontMetrics().horizontalAdvance("9") * digits

    def _update_line_number_area_width(
        self,
    ) -> None:
        """
        Actualiza el margen izquierdo del editor
        para reservar espacio al área de números
        de línea.
        """

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
        """
        Actualiza el área de números de línea
        cuando el editor se desplaza o repinta.

        Args:
            rect:
                Región afectada por la actualización.

            dy:
                Desplazamiento vertical aplicado
                al contenido.
        """

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

    def _highlight_current_line(
        self,
    ) -> None:
        """
        Resalta visualmente la línea donde se
        encuentra el cursor.
        """

        selections = []

        if not self.isReadOnly():

            selection = QTextEdit.ExtraSelection()

            selection.format.setBackground(
                QColor(
                    ThemeManager.get_color(
                        "sql_editor_current_line_background_color",
                    )
                )
            )

            selection.format.setProperty(
                QTextFormat.Property.FullWidthSelection,
                True,
            )

            selection.cursor = self.textCursor()

            # Evitar seleccionar texto
            selection.cursor.clearSelection()

            selections.append(selection)

        self.setExtraSelections(selections)

        self.line_number_area.update()

    # ===============
    # === SIGNALS ===
    # ===============

    def _connect_signals(
        self,
    ) -> None:
        """
        Conecta las señales del editor con
        sus handlers correspondientes.
        """

        self.blockCountChanged.connect(
            self._update_line_number_area_width,
        )

        self.updateRequest.connect(
            self._update_line_number_area,
        )

        self.cursorPositionChanged.connect(
            self._highlight_current_line,
        )

    # =====================
    # === EVENT HELPERS ===
    # =====================

    def _emit_execute_requested(
        self,
        scope: SqlScope,
    ) -> None:
        """
        Emite la solicitud de ejecución del SQL
        correspondiente al ámbito especificado.

        Args:
            scope (SqlScope):
                Alcance del texto que debe
                ejecutarse.
        """

        sql = self._get_sql(scope)

        if sql is not None:

            if scope == SqlScope.SELECTED_TEXT:

                self.execute_requested.emit(
                    [sql],
                    scope,
                )

            elif scope == SqlScope.FULL_SCRIPT:

                self.execute_requested.emit(
                    self._split_sql_statements(sql),
                    scope,
                )

    # ====================
    # === QT OVERRIDES ===
    # ====================

    def keyPressEvent(
        self,
        event: QKeyEvent,
    ) -> None:
        """
        Gestiona combinaciones de teclas
        específicas del editor SQL.

        Args:
            event (QKeyEvent):
                Evento de teclado recibido.
        """

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

    def resizeEvent(
        self,
        event: QResizeEvent,
    ) -> None:
        """
        Reposiciona el área de números de línea
        cuando cambia el tamaño del editor.

        Args:
            event:
                Evento de redimensionamiento
                recibido desde Qt.
        """

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

        Args:
            text (str):
                Texto a evaluar.

        Returns:
            bool:
                - `True` si existe contenido útil.
                - `False` en caso contrario.
        """

        return bool(text.strip())

    def _get_sql(
        self,
        scope: SqlScope,
    ) -> str | None:
        """
        Obtiene el texto SQL correspondiente
        al ámbito solicitado.

        Args:
            scope (SqlScope):
                Alcance del texto que se desea
                recuperar.

        Returns:
            str | None:
                Texto SQL normalizado o `None`
                si no existe contenido.
        """

        if scope == SqlScope.SELECTED_TEXT:
            text = self.textCursor().selectedText()

        elif scope == SqlScope.FULL_SCRIPT:
            text = self.toPlainText()

        else:
            return None

        return self._normalize_sql(text) if self._has_content(text) else None

    @staticmethod
    def _normalize_sql(
        text: str,
    ) -> str:
        """
        Convierte caracteres especiales utilizados
        por Qt en saltos de línea convencionales.

        Args:
            text (str):
                Texto original.

        Returns:
            str:
                Texto normalizado.
        """

        return text.replace("\u2029", "\n").replace("\r\n", "\n").replace("\r", "\n")

    @staticmethod
    def _split_sql_statements(
        sql: str,
    ) -> list[str]:
        """
        Divide un script SQL en sentencias
        individuales.

        Cada sentencia conserva su contenido y se
        eliminan los espacios en blanco al principio
        y al final.

        Args:
            sql (str):
                Script SQL que se desea dividir.

        Returns:
            list[str]:
                Lista de sentencias SQL obtenidas.
        """

        statements = []

        for statement in sqlparse.split(sql):
            cleaned_statement = statement.strip()

            if cleaned_statement:
                statements.append(cleaned_statement)

        return statements

    # ==================
    # === PUBLIC API ===
    # ==================

    def line_number_area_paint_event(
        self,
        event: QPaintEvent,
    ) -> None:
        """
        Dibuja los números de línea visibles
        en el área lateral del editor.

        Args:
            event:
                Evento de pintado recibido desde
                el widget de numeración.
        """

        painter = QPainter(self.line_number_area)

        painter.fillRect(
            event.rect(),
            QColor(
                ThemeManager.get_color(
                    "sql_editor_line_number_background_color",
                )
            ),
        )

        block = self.firstVisibleBlock()

        block_number = block.blockNumber()

        top = round(
            self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        )

        bottom = top + round(self.blockBoundingRect(block).height())

        current_block = self.textCursor().blockNumber()

        while block.isValid() and top <= event.rect().bottom():

            if block.isVisible() and bottom >= event.rect().top():

                number = str(block_number + 1)

                if block_number == current_block:

                    painter.setPen(
                        QColor(
                            ThemeManager.get_color(
                                "sql_editor_current_line_number_color",
                            )
                        )
                    )

                else:

                    painter.setPen(
                        QColor(
                            ThemeManager.get_color(
                                "sql_editor_line_number_color",
                            )
                        )
                    )

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

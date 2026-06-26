import sqlparse
from PySide6.QtCore import QRectF, Qt, Signal
from PySide6.QtGui import (
    QColor,
    QKeyEvent,
    QPainter,
    QPainterPath,
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
        self.line_number_area.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.line_number_area.setAutoFillBackground(False)

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

    def paintEvent(
        self,
        event: QPaintEvent,
    ) -> None:
        """
        Dibuja el contenido del editor.

        Antes de delegar el pintado del texto a
        ``QPlainTextEdit``, se dibuja manualmente
        el fondo de la línea donde se encuentra
        el cursor.

        Este enfoque sustituye al uso de
        ``ExtraSelection`` para el resaltado de
        la línea actual, proporcionando un
        resultado visual más uniforme y evitando
        el efecto de "rectángulo superpuesto"
        generado por ``FullWidthSelection``.

        Args:
            event:
                Evento de pintado recibido desde
                Qt.
        """

        # Crear un painter asociado únicamente al
        # viewport del editor, que es la zona donde
        # se dibuja el contenido del documento.
        painter = QPainter(self.viewport())

        # Obtener el bloque (una línea lógica del
        # documento) donde se encuentra el cursor.
        block = self.textCursor().block()

        # Obtener el rectángulo ocupado por el
        # bloque dentro del viewport, teniendo en
        # cuenta el desplazamiento del contenido.
        rect = (
            self.blockBoundingGeometry(block).translated(self.contentOffset()).toRect()
        )

        # Ajustar la altura al alto real de la
        # fuente para evitar pequeños desfases
        # verticales producidos por el layout del
        # documento.
        rect.setHeight(self.fontMetrics().height())

        # Obtener el color configurado para el
        # resaltado de la línea actual.
        color = QColor(
            ThemeManager.get_color("sql_editor_current_line_background_color")
        )

        # Pintar el fondo de la línea antes de que
        # Qt dibuje el texto, de forma que el texto
        # quede visible por encima del resaltado.
        painter.fillRect(rect, color)

        # Delegar el resto del proceso de pintado
        # al comportamiento estándar del editor.
        super().paintEvent(event)

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
        Dibuja el área lateral de números de línea.

        Args:
            event (QPaintEvent):
                Evento de pintado recibido desde
                el widget de numeración.
        """

        # Crear el painter asociado al área
        # de numeración.
        painter = QPainter(self.line_number_area)

        # Dibujar el fondo del panel lateral.
        self._paint_line_number_background(
            painter,
        )

        # Dibujar los números de las líneas
        # visibles.
        self._paint_line_numbers(
            painter,
            event,
        )

    def _paint_line_number_background(
        self,
        painter: QPainter,
    ) -> None:
        """
        Dibuja el fondo del área de numeración
        con las esquinas izquierdas redondeadas.

        Args:
            painter (QPainter):
                Painter utilizado para el dibujado.
        """

        # Radio de las esquinas
        # redondeadas del panel.
        radius = 8

        # Área completa del panel lateral.
        rect = QRectF(self.line_number_area.rect())

        # Construir el contorno del panel.
        # Solo las esquinas izquierdas se
        # redondean.
        path = QPainterPath()

        path.moveTo(
            rect.right(),
            rect.top(),
        )

        path.lineTo(
            rect.left() + radius,
            rect.top(),
        )
        path.quadTo(
            rect.left(),
            rect.top(),
            rect.left(),
            rect.top() + radius,
        )

        path.lineTo(
            rect.left(),
            rect.bottom() - radius,
        )
        path.quadTo(
            rect.left(),
            rect.bottom(),
            rect.left() + radius,
            rect.bottom(),
        )

        path.lineTo(
            rect.right(),
            rect.bottom(),
        )

        # Cerrar el contorno para
        # completar la figura.
        path.closeSubpath()

        # Limitar el área de pintado al
        # contorno definido.
        painter.setClipPath(path)

        # Suavizar los bordes redondeados.
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # Desactivar el contorno para dibujar
        # únicamente el relleno del panel.
        painter.setPen(Qt.PenStyle.NoPen)

        # Dibujar el fondo del panel.
        painter.setBrush(
            QColor(
                ThemeManager.get_color("sql_editor_line_number_background_color"),
            )
        )

        painter.drawPath(path)

        # Dibujar el separador entre el panel y el editor.
        painter.setPen(
            QColor(
                ThemeManager.get_color(
                    "sql_editor_border_color",
                )
            )
        )

        # Última columna del panel.
        x = self.line_number_area.width() - 1

        painter.drawLine(
            x,
            0,
            x,
            self.line_number_area.height(),
        )

    def _paint_line_numbers(
        self,
        painter: QPainter,
        event: QPaintEvent,
    ) -> None:
        """
        Dibuja los números de línea visibles.

        Args:
            painter (QPainter):
                Painter utilizado para el dibujado.

            event (QPaintEvent):
                Evento de pintado recibido desde
                el widget de numeración.
        """

        # Primer bloque actualmente visible.
        block = self.firstVisibleBlock()

        block_number = block.blockNumber()

        # Coordenadas verticales del bloque
        # dentro del viewport.
        top = round(
            self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        )

        bottom = top + round(self.blockBoundingRect(block).height())

        # Bloque donde se encuentra el cursor.
        current_block = self.textCursor().blockNumber()

        # Recorrer únicamente los bloques visibles.
        while block.isValid() and top <= event.rect().bottom():

            if block.isVisible() and bottom >= event.rect().top():

                number = str(block_number + 1)

                # Resaltar el número de la línea actual.
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

                # Dibujar el número alineado a la derecha.
                painter.drawText(
                    0,
                    top,
                    self.line_number_area.width() - 5,
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight,
                    number,
                )

            # Avanzar al siguiente bloque del
            # documento y actualizar su posición.
            block = block.next()

            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())

            block_number += 1

import sqlparse
from PySide6.QtCore import (
    QRectF,
    Qt,
    Signal,
)
from PySide6.QtGui import (
    QColor,
    QKeyEvent,
    QPainter,
    QPainterPath,
    QPaintEvent,
    QResizeEvent,
    QTextFormat,
)
from PySide6.QtWidgets import (
    QPlainTextEdit,
    QTextEdit,
)

from entities.file import File
from entities.sql_scope import SqlScope
from ui.themes.theme_manager import ThemeManager
from ui.widgets.workspace.sql_editor.line_number_area import LineNumberArea
from ui.widgets.workspace.sql_editor.sql_completer import SqlCompleter
from ui.widgets.workspace.sql_editor.sql_highlighter import SqlHighlighter


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
    file_modified = Signal(File)
    save_changes = Signal(File)
    rename_file = Signal(File)

    # ============
    # === INIT ===
    # ============

    def __init__(
        self,
        file: File,
    ) -> None:
        """
        Inicializa el editor sql.

        Args:
            file (File):
                Archivo abierto asociado al editor.
        """

        super().__init__()

        self.setObjectName("sql_editor")

        self.file = file

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

        self.setPlainText(self.file.content)

        self.verticalScrollBar().setSingleStep(1)
        self.horizontalScrollBar().setSingleStep(1)

        self.line_number_area = LineNumberArea(self)
        self.line_number_area.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.line_number_area.setAutoFillBackground(False)

        self._update_line_number_area_width()

        # Inicializar el resaltado de la línea actual.
        self._highlight_current_line()

        # Resaltado de sintaxis
        self.syntax_highlighter = SqlHighlighter(self.document())

        # Autocompleción de sql
        self.completer = SqlCompleter(parent_widget=self)

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
        Resalta la línea donde se encuentra el cursor.

        El resaltado se implementa mediante
        ``QTextEdit.ExtraSelection`` con la propiedad
        ``FullWidthSelection`` para cubrir todo el
        ancho visible del editor.

        El resaltado se actualiza automáticamente cada
        vez que cambia la posición del cursor.
        """

        selection = QTextEdit.ExtraSelection()

        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()

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

        self.setExtraSelections([selection])

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

        # Actualizar el resaltado cuando cambia el cursor.
        self.cursorPositionChanged.connect(
            self._highlight_current_line,
        )

        self.textChanged.connect(
            self._on_text_changed,
        )

    # ======================
    # === EVENT HANDLERS ===
    # ======================

    def _on_text_changed(
        self,
    ) -> None:
        """
        Gestiona la modificación del contenido del editor.

        Actualiza el contenido del archivo asociado, notifica
        que el archivo ha sido modificado y refresca las
        sugerencias dinámicas del autocompletador.
        """

        text = self.toPlainText()

        self.file.content = text

        self.file_modified.emit(self.file)

        self.completer.update_document_completion(
            text,
        )

    # =====================
    # === EVENT HELPERS ===
    # =====================

    def execute(
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

        if sql is None:
            return

        self.execute_requested.emit(
            self._split_sql_statements(sql),
            scope,
        )

    def text_under_cursor(
        self,
    ) -> str:
        """
        Obtiene la palabra situada bajo el cursor.

        Considera ':', '_' y '@' como parte de una palabra
        para soportar parámetros y variables SQL.

        Returns:
            str:
                Texto de la palabra sobre la que se
                encuentra el cursor. Si no existe,
                devuelve una cadena vacía.
        """

        cursor = self.textCursor()

        pos = cursor.position()
        text = self.toPlainText()

        start = pos

        while start > 0:
            c = text[start - 1]

            if c.isalnum() or c in "_:@":
                start -= 1
            else:
                break

        return text[start:pos]

    def _handle_completer_popup_key_event(
        self,
        event: QKeyEvent,
    ) -> bool:
        """
        Permite que el popup del autocompletador
        gestione determinadas teclas cuando está visible.

        Args:
            event (QKeyEvent):
                Evento de teclado recibido.

        Returns:
            bool:
                ``True`` si el evento ha sido gestionado
                por el popup y no debe seguir procesándose.
        """

        if not self.completer.popup().isVisible():
            return False

        if event.key() in (
            Qt.Key.Key_Escape,
            Qt.Key.Key_Tab,
        ):
            event.ignore()
            return True

        return False

    def _update_completer(
        self,
        event: QKeyEvent,
    ) -> None:
        """
        Actualiza el estado del autocompletador tras
        una pulsación de teclado.

        Obtiene el prefijo situado bajo el cursor y,
        si corresponde, actualiza y muestra el popup
        de sugerencias. En caso contrario, lo oculta.

        Args:
            event (QKeyEvent):
                Evento de teclado recibido.
        """

        popup_visible = self.completer.popup().isVisible()

        # Evitar que el popup aparezca al borrar texto
        # si todavía no estaba visible.
        if not popup_visible and event.key() in (
            Qt.Key.Key_Backspace,
            Qt.Key.Key_Delete,
        ):
            return

        # Ctrl + Space: Fuerza la aparicion del popup
        # de autocompletado.
        is_shortcut = (
            event.modifiers() & Qt.KeyboardModifier.ControlModifier
            and event.key() == Qt.Key.Key_Space
        )

        completion_prefix = self.text_under_cursor()

        if not is_shortcut and (len(completion_prefix) < 1 or not event.text()):
            self.completer.popup().hide()
            return

        self.completer.complete_at(
            prefix=completion_prefix,
            rect=self.cursorRect(),
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

        if self._handle_completer_popup_key_event(event):
            return

        modifiers = event.modifiers()

        # Tab -> 4 espacios.
        if event.key() == Qt.Key.Key_Tab:
            self.insertPlainText("    ")
            return

        # Ctrl + Shift + Enter -> Ejecutar script.
        if (
            event.key() == Qt.Key.Key_Return
            and modifiers & Qt.KeyboardModifier.ControlModifier
            and modifiers & Qt.KeyboardModifier.ShiftModifier
        ):
            self.execute(SqlScope.FULL_SCRIPT)
            return

        # Ctrl + Alt + Enter -> Ejecutar texto seleccionado.
        if (
            event.key() == Qt.Key.Key_Return
            and modifiers & Qt.KeyboardModifier.ControlModifier
            and modifiers & Qt.KeyboardModifier.AltModifier
        ):
            self.execute(SqlScope.SELECTED_TEXT)
            return

        # Ctrl + Enter -> Ejecutar consulta actual.
        if (
            event.key() == Qt.Key.Key_Return
            and modifiers & Qt.KeyboardModifier.ControlModifier
        ):
            self.execute(SqlScope.ACTUAL_QUERY)
            return

        # Ctrl + S -> Guardar cambios.
        if (
            event.key() == Qt.Key.Key_S
            and modifiers & Qt.KeyboardModifier.ControlModifier
        ):
            self.save_changes.emit(self.file)
            return

        # Ctrl + R -> Renombrar archivo.
        if (
            event.key() == Qt.Key.Key_R
            and modifiers & Qt.KeyboardModifier.ControlModifier
        ):
            self.rename_file.emit(self.file)
            return

        # Shift + Tab -> No hacer nada.
        if event.key() == Qt.Key.Key_Backtab:
            event.accept()
            return

        super().keyPressEvent(event)

        self._update_completer(event)

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

        elif scope == SqlScope.ACTUAL_QUERY:
            text = self._get_current_query()

        elif scope == SqlScope.FULL_SCRIPT:
            text = self.toPlainText()

        else:
            return None

        return self._normalize_sql(text) if self._has_content(text) else None

    def _get_current_query(
        self,
    ) -> str | None:
        """
        Obtiene la sentencia SQL sobre la que se encuentra
        actualmente el cursor.

        Returns:
            str | None:
                Sentencia SQL normalizada o ``None`` si no se
                encuentra ninguna consulta válida.
        """

        text = self.toPlainText()

        if not self._has_content(text):
            return None

        cursor_position = self.textCursor().position()

        offset = 0

        for statement in sqlparse.parse(text):

            statement_text = str(statement)

            start = text.find(
                statement_text,
                offset,
            )

            if start == -1:
                continue

            end = start + len(statement_text)

            # Ignorar espacios y saltos de línea
            # exteriores a la sentencia.
            leading = len(statement_text) - len(statement_text.lstrip())
            trailing = len(statement_text) - len(statement_text.rstrip())

            statement_start = start + leading
            statement_end = end - trailing

            if statement_start <= cursor_position <= statement_end:

                statement_text = statement_text.strip()

                return self._normalize_sql(statement_text)

            offset = end

        return None

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
        radius = 4

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

    def insert_query_at_cursor(
        self,
        text: str,
    ) -> None:
        """
        Inserta un fragmento de texto SQL en la posición
        actual del cursor, reemplazando la selección si existe.

        Args:
            text (str): Texto SQL a insertar.
        """

        if not text:
            return

        # Insertar el texto en la posición del cursor actual
        self.insertPlainText(text)

        # Asegurar que el editor recupere el foco visual
        self.setFocus()

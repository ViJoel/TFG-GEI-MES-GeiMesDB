from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QFontMetrics,
    QTextCursor,
)
from PySide6.QtWidgets import (
    QCompleter,
    QWidget,
)

from ui.widgets.workspace.sql_editor.sql_completer_model import SqlCompleterModel

if TYPE_CHECKING:
    from PySide6.QtCore import QRect
    from PySide6.QtWidgets import QPlainTextEdit


class SqlCompleter(QCompleter):
    """
    Autocompletador SQL basado en ``QCompleter``.

    Gestiona la configuración del popup de autocompletado
    y utiliza un ``SqlCompleterModel`` como origen de los
    datos mostrados al usuario.
    """

    # =================
    # === VARIABLES ===
    # =================

    _POPUP_HORIZONTAL_MARGIN = 20

    # ============
    # === INIT ===
    # ============

    def __init__(
        self,
        parent_widget: QWidget,
    ) -> None:
        """
        Inicializa el autocompletador SQL y su
        modelo de datos.

        Args:
            parent_widget (QWidget):
                Widget sobre el que actuará el
                autocompletador.
        """

        super().__init__()

        self._model = SqlCompleterModel()

        self._setup_ui(parent_widget)
        self._connect_signals()

    # ================
    # === UI SETUP ===
    # ================

    def _setup_ui(
        self,
        parent_widget: QWidget,
    ) -> None:
        """
        Configura el autocompletador y su popup.
        """

        self.popup().setObjectName("sql_completer_popup")

        self.setModel(self._model)
        self.setWidget(parent_widget)
        self.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

    # ===============
    # === SIGNALS ===
    # ===============

    def _connect_signals(
        self,
    ) -> None:
        """
        Conecta señales de widgets
        con sus handlers correspondientes.
        """

        self.activated[str].connect(
            self.insert_completion,
        )

    # ==================
    # === PUBLIC API ===
    # ==================

    def popup_width(
        self,
    ) -> int:
        """
        Calcula el ancho necesario para mostrar
        completamente la sugerencia más larga del
        autocompletador.

        Returns:
            int:
                Ancho recomendado del popup, incluyendo
                un margen adicional para evitar recortes.
        """

        metrics = QFontMetrics(self.popup().font())

        width = 0

        for row in range(self._model.rowCount()):

            text = self._model.item(row).text()

            width = max(
                width,
                metrics.horizontalAdvance(text),
            )

        return width + self._POPUP_HORIZONTAL_MARGIN

    def refresh(
        self,
    ) -> None:
        """
        Recarga el modelo de datos del autocompletador.
        """

        self._model.refresh()

    def insert_completion(
        self,
        completion: str,
    ) -> None:
        """
        Inserta la sugerencia seleccionada
        sustituyendo la palabra situada bajo
        el cursor.

        Args:
            completion (str):
                Texto seleccionado en el
                autocompletador.
        """

        editor: QPlainTextEdit = self.widget()

        if editor is None:
            return

        tc = editor.textCursor()

        pos = tc.position()
        text = editor.toPlainText()

        start = pos

        while start > 0:
            c = text[start - 1]

            if c.isalnum() or c in "_:@":
                start -= 1
            else:
                break

        tc.setPosition(start)
        tc.setPosition(pos, QTextCursor.MoveMode.KeepAnchor)

        tc.insertText(completion)

        editor.setTextCursor(tc)

    def complete_at(
        self,
        prefix: str,
        rect: QRect,
    ) -> None:
        """
        Actualiza el prefijo de búsqueda y
        muestra el popup de autocompletado.

        Args:
            prefix (str):
                Texto utilizado para filtrar
                las sugerencias.

            rect:
                Rectángulo donde debe mostrarse
                el popup.
        """

        if prefix != self.completionPrefix():

            self.setCompletionPrefix(prefix)

            self.popup().setCurrentIndex(self.completionModel().index(0, 0))

        rect.setWidth(self.popup_width())

        self.complete(rect)

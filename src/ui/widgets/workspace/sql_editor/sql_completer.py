import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QColor,
    QFontMetrics,
    QStandardItem,
    QStandardItemModel,
    QTextCursor,
)
from PySide6.QtWidgets import (
    QApplication,
    QCompleter,
    QMainWindow,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ui.widgets.workspace.sql_editor.sql_completer_model import SqlCompleterModel


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
        Inicializa el autocompletador SQL.

        Args:
            parent_widget (QWidget):
                Widget sobre el que actuará el autocompletador.
        """

        super().__init__()

        self._model = SqlCompleterModel()

        self.setModel(self._model)
        self.setWidget(parent_widget)
        self.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

    # ================
    # === UI SETUP ===
    # ================

    # ================
    # === UI STATE ===
    # ================

    # ==================
    # === UI HELPERS ===
    # ==================

    # ===============
    # === SIGNALS ===
    # ===============

    # ======================
    # === EVENT HANDLERS ===
    # ======================

    # =====================
    # === EVENT HELPERS ===
    # =====================

    # ====================
    # === QT OVERRIDES ===
    # ====================

    # ===================
    # === PRIVATE API ===
    # ===================

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

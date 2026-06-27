from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPaintEvent
from PySide6.QtWidgets import QWidget

if TYPE_CHECKING:
    from ui.widgets.workspace.sql_editor.sql_editor import SqlEditor


class LineNumberArea(QWidget):
    """
    Widget auxiliar encargado de representar
    el área lateral donde se muestran los
    números de línea del editor SQL.

    Responsabilidades:
    - Reservar el espacio necesario para
      los números de línea.
    - Delegar el proceso de pintado en
      el editor asociado.
    """

    # ============
    # === INIT ===
    # ============

    def __init__(
        self,
        editor: SqlEditor,
    ) -> None:
        """
        Inicializa el área de números
        de línea asociada a un editor.

        Args:
            editor (SqlEditor):
                Editor propietario encargado
                del cálculo y pintado del área.
        """

        super().__init__(editor)

        self.setObjectName("sql_editor_line_number_area")

        self.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground,
            True,
        )

        self.editor = editor

    # ==================
    # === PUBLIC API ===
    # ==================

    def sizeHint(
        self,
    ) -> QSize:
        """
        Retorna el tamaño recomendado para
        el área de números de línea.

        Returns:
            QSize:
                Tamaño sugerido para el widget.
        """

        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(
        self,
        event: QPaintEvent,
    ) -> None:
        """
        Solicita al editor asociado el
        pintado del área de números de línea.

        Args:
            event (QPaintEvent):
                Evento de pintado recibido
                por Qt.
        """

        self.editor.line_number_area_paint_event(event)

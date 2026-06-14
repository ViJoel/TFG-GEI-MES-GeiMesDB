from PySide6.QtGui import QColor, Qt
from PySide6.QtWidgets import (
    QListWidget,
    QListWidgetItem,
)
from PySide6.QtGui import QFont
from entities.script_result_data import ScriptResultData


class ScriptResult(QListWidget):

    # ============
    # === INIT ===
    # ============

    def __init__(self) -> None:

        super().__init__()

        self._setup_ui()

    # ================
    # === UI SETUP ===
    # ================

    def _setup_ui(self) -> None:
        """
        Construye la interfaz principal del widget.
        """

        self.setSpacing(8)

        # No permitir selección
        self.setSelectionMode(self.SelectionMode.NoSelection)

        # No permitir editar ni arrastrar
        self.setFocusPolicy(Qt.NoFocus)

        # Mostrar varias líneas correctamente
        self.setWordWrap(True)

        font = QFont("Consolas")
        font.setPointSize(10)

        self.setFont(font)

    # ==================
    # === PUBLIC API ===
    # ==================

    def show_script_result(
        self,
        script_result_data: ScriptResultData,
    ) -> None:

        self.clear()

        for item in script_result_data.items:

            if item.success:

                text = item.query
                color = QColor("green")

            else:

                text = f"{item.query}\n" f"Error: {item.error}"

                color = QColor("red")

            qlwi = QListWidgetItem(text)

            qlwi.setForeground(color)

            self.addItem(qlwi)

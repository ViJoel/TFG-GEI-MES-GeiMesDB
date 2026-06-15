from PySide6.QtGui import QColor, QFont, QTextCursor
from PySide6.QtWidgets import QPlainTextEdit, QTextEdit

from entities.script_result import ScriptResult


class Console(QTextEdit):

    # =================
    # === VARIABLES ===
    # =================

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

        self.setReadOnly(True)

        font = QFont("Consolas")
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)

        pass

    # ===================
    # === PRIVATE API ===
    # ===================

    def _append_colored_text(
        self,
        text: str,
        color: QColor,
    ) -> None:

        self.moveCursor(QTextCursor.MoveOperation.End)

        self.setTextColor(color)

        self.insertPlainText(text)

        self.moveCursor(QTextCursor.MoveOperation.End)

    # ==================
    # === PUBLIC API ===
    # ==================

    def clear_output(self) -> None:

        self.clear()

    def write(
        self,
        text: str,
    ) -> None:

        self._append_colored_text(
            text=text,
            color=QColor("white"),
        )

    def write_success(
        self,
        text: str,
    ) -> None:

        self._append_colored_text(
            text=text,
            color=QColor("green"),
        )

    def write_error(
        self,
        text: str,
    ) -> None:

        self._append_colored_text(
            text=text,
            color=QColor("red"),
        )

    def show_script_result(
        self,
        script_result: ScriptResult,
    ) -> None:

        self.clear()

        if script_result is None:
            return

        for item in script_result.items:

            if item.success:

                self.write_success(f"{item.query}\n")

            else:

                self.write_error(f"{item.query}\n" f"Error: {item.error}\n")

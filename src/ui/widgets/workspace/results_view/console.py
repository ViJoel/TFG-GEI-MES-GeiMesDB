from PySide6.QtGui import QColor, QTextCursor
from PySide6.QtWidgets import QTextEdit

from entities.script_result import ScriptResult
from ui.themes.theme_manager import ThemeManager


class Console(QTextEdit):
    """
    Widget utilizado para mostrar mensajes y
    resultados de ejecución en formato de consola.
    """

    # ============
    # === INIT ===
    # ============

    def __init__(
        self,
    ) -> None:
        """
        Inicializa el widget de consola.
        """

        super().__init__()

        self.setObjectName("console")

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

        self.setReadOnly(True)

    # ===================
    # === PRIVATE API ===
    # ===================

    def _append_colored_text(
        self,
        text: str,
        color: QColor,
    ) -> None:
        """
        Añade texto a la consola utilizando el
        color especificado.

        Args:
            text (str):
                Texto que se añadirá a la consola.

            color (QColor):
                Color con el que se mostrará el
                texto.
        """

        self.moveCursor(QTextCursor.MoveOperation.End)

        self.setTextColor(color)

        self.insertPlainText(text)

        self.moveCursor(QTextCursor.MoveOperation.End)

    # ==================
    # === PUBLIC API ===
    # ==================

    def clear_output(
        self,
    ) -> None:
        """
        Elimina todo el contenido mostrado en la
        consola.
        """

        self.clear()

    def write(
        self,
        text: str,
    ) -> None:
        """
        Escribe texto en color blanco.

        Args:
            text (str):
                Texto que se mostrará en la consola.
        """

        self._append_colored_text(
            text=text,
            color=QColor(ThemeManager.get_color("console_color")),
        )

    def write_success(
        self,
        text: str,
    ) -> None:
        """
        Escribe texto en color verde.

        Args:
            text (str):
                Texto que se mostrará en la consola.
        """

        self._append_colored_text(
            text=text,
            color=QColor(ThemeManager.get_color("console_success_color")),
        )

    def write_error(
        self,
        text: str,
    ) -> None:
        """
        Escribe texto en color rojo.

        Args:
            text (str):
                Texto que se mostrará en la consola.
        """

        self._append_colored_text(
            text=text,
            color=QColor(ThemeManager.get_color("console_error_color")),
        )

    def show_script_result(
        self,
        script_result: ScriptResult,
    ) -> None:
        """
        Muestra en la consola el resultado de la
        ejecución de un script.

        Args:
            script_result (ScriptResult):
                Resultado de la ejecución del
                script.
        """

        self.clear()

        if script_result is None:
            return

        for item in script_result.items:

            if item.success:
                self.write_success(f"{item.query}\n\n")

            else:
                self.write_error(f"{item.query}\nError: {item.error}\n\n")

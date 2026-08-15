from PySide6.QtGui import (
    QColor,
    QTextCursor,
)
from PySide6.QtWidgets import QTextEdit

from entities.message_type import MessageType
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

        self.verticalScrollBar().setSingleStep(20)
        self.horizontalScrollBar().setSingleStep(20)

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
        message_type: MessageType = MessageType.DEFAULT,
    ) -> None:
        """
        Escribe texto en el color correspondiente.

        Args:
            text (str):
                Texto que se mostrará en la consola.

            message_type (MessageType):
                Tipo de mensaje.
        """

        string_1 = "console_"

        match message_type:

            case MessageType.DEFAULT:
                string_2 = "default"

            case MessageType.DISABLED:
                string_2 = "disabled"

            case MessageType.INFO:
                string_2 = "info"

            case MessageType.SUCCESS:
                string_2 = "success"

            case MessageType.WARNING:
                string_2 = "warning"

            case MessageType.ERROR:
                string_2 = "error"

        string_3 = "_color"

        color_name = string_1 + string_2 + string_3

        self._append_colored_text(
            text=text,
            color=QColor(ThemeManager.get_color(color_name)),
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

        last_index = len(script_result.items) - 1

        for index, item in enumerate(script_result.items):

            if item.success:
                self.write(
                    f"{item.query}\n\n",
                    MessageType.SUCCESS,
                )

            else:
                self.write(
                    f"{item.query}\n\nError: {item.error}\n\n",
                    MessageType.ERROR,
                )

            if index != last_index:
                self.write(
                    "-" * 80 + "\n\n",
                    MessageType.DISABLED,
                )

        if script_result.rolled_back:

            self.write(
                "=" * 80
                + "\n"
                + self.tr("One or more UPDATE operations failed.")
                + "\n"
                + self.tr("The transaction was rolled back.")
                + "\n"
                + self.tr("No changes were saved."),
                MessageType.INFO,
            )

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialogButtonBox,
    QInputDialog,
)


class RenameFileDialog(QInputDialog):

    # ============
    # === INIT ===
    # ============

    def __init__(
        self,
        current_name: str,
        parent=None,
    ) -> None:

        super().__init__(parent)

        self.current_name = current_name

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

        self.setWindowTitle("Rename file")
        self.setLabelText("New file name:")
        self.setTextValue(self.current_name)

        # Quitamos los bordes y la barra de
        # título nativa del sistema operativo.
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)

        # Márgenes y espaciado del layout interno.
        if self.layout():
            self.layout().setContentsMargins(20, 20, 20, 20)
            self.layout().setSpacing(12)

    # ==================
    # === UI HELPERS ===
    # ==================

    def _setup_buttons_styles(
        self,
    ) -> None:

        button_box = self.findChild(QDialogButtonBox)

        if button_box:

            ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
            cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)

            if ok_button:

                ok_button.setProperty(
                    "type",
                    "primary",
                )

                ok_button.setText(
                    ok_button.text().replace(
                        "&",
                        "",
                    )
                )

                # --- FORZAR REEVALUACIÓN DE ESTILOS QSS ---
                ok_button.style().unpolish(ok_button)
                ok_button.style().polish(ok_button)
                ok_button.update()

            if cancel_button:

                cancel_button.setProperty(
                    "type",
                    "danger",
                )

                cancel_button.setText(
                    cancel_button.text().replace(
                        "&",
                        "",
                    )
                )

                # --- FORZAR REEVALUACIÓN DE ESTILOS QSS ---
                cancel_button.style().unpolish(cancel_button)
                cancel_button.style().polish(cancel_button)
                cancel_button.update()

    # ====================
    # === QT OVERRIDES ===
    # ====================

    def showEvent(
        self,
        event,
    ):

        super().showEvent(event)

        # Aplicamos y refrescamos los estilos de los
        # botones en el showEvent para garantizar que
        # el selector QSS con [type="..."] se aplique
        # correctamente.
        self._setup_buttons_styles()

        parent = self.parentWidget()

        if parent and parent.isVisible():

            # Posición global del widget padre en la pantalla.
            parent_geo = parent.geometry()
            parent_global_pos = parent.mapToGlobal(parent_geo.topLeft())

            # Centrado exacto usando las dimensiones renderizadas.
            x = parent_global_pos.x() + (parent.width() - self.width()) // 2
            y = parent_global_pos.y() + (parent.height() - self.height()) // 2

            self.move(x, y)

    # ==================
    # === PUBLIC API ===
    # ==================

    @classmethod
    def get_new_name(
        cls,
        current_name: str,
        parent=None,
    ) -> str | None:

        dialog = cls(current_name, parent)

        if dialog.exec() == QInputDialog.DialogCode.Accepted:
            new_name = dialog.textValue().strip()
            return new_name if new_name else None

        return None

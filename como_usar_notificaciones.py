from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget

from ui.widgets.notifications.notification import (
    Notification,
    NotificationType,
)


class ExampleWindow(QWidget):

    def __init__(self):
        super().__init__()

        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Botón de información
        info_button = QPushButton("Mostrar INFO")
        info_button.clicked.connect(self._show_info_notification)

        # Botón de éxito
        success_button = QPushButton("Mostrar SUCCESS")
        success_button.clicked.connect(self._show_success_notification)

        # Botón de error
        error_button = QPushButton("Mostrar ERROR")
        error_button.clicked.connect(self._show_error_notification)

        layout.addWidget(info_button)
        layout.addWidget(success_button)
        layout.addWidget(error_button)

    # ======================
    # === NOTIFICATIONS ===
    # ======================

    def _show_info_notification(self) -> None:
        notification = Notification(
            NotificationType.INFO,
            "Conexiones cargadas correctamente",

            # self.window() devuelve la ventana principal
            # a la que pertenece este widget.
            #
            # Esto evita que la notificación aparezca
            # como una ventana independiente del sistema.
            parent=self.window(),
        )

        notification.move(20, 20)
        notification.show()

    def _show_success_notification(self) -> None:
        notification = Notification(
            NotificationType.SUCCESS,
            "Base de datos conectada",
            parent=self.window(),
        )

        notification.move(20, 80)
        notification.show()

    def _show_error_notification(self) -> None:
        notification = Notification(
            NotificationType.ERROR,
            "No se pudo establecer la conexión",
            parent=self.window(),
        )

        notification.move(20, 140)
        notification.show()


if __name__ == "__main__":
    app = QApplication([])

    window = ExampleWindow()
    window.resize(400, 300)
    window.show()

    app.exec()
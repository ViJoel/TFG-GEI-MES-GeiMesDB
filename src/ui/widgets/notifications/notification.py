import qtawesome as qta
from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QSizePolicy,
    QWidget,
)

from ui.utils.layouts import hbox
from ui.widgets.notifications.notifications_type import NotificationType
from PySide6.QtCore import Qt


class Notification(QWidget):

    # ============
    # === INIT ===
    # ============

    def __init__(
        self,
        notification_type: NotificationType,
        message: str,
        parent=None,
    ):
        super().__init__(parent)

        self.notification_type = notification_type
        self.message = message

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.ToolTip)

        self._setup_ui()

    # ================
    # === UI SETUP ===
    # ================

    def _setup_ui(self) -> None:
        """
        Configura la interfaz de la notificación.
        """

        # Layout principal
        main_layout = hbox()
        self.setLayout(main_layout)

        # Política de tamaño
        self.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Fixed,
        )

        # Icono
        icon_label = QLabel()

        icon_label.setPixmap(
            qta.icon(
                self._get_icon_name(),
            ).pixmap(18, 18)
        )

        # Texto
        message_label = QLabel(f"[{self.notification_type.value}] {self.message}")

        # Botón cerrar
        close_button = QPushButton()

        close_button.setIcon(qta.icon("fa5s.times"))

        close_button.clicked.connect(self.close)

        # Añadir widgets
        main_layout.addWidget(icon_label)
        main_layout.addWidget(message_label)
        main_layout.addWidget(close_button)

    # ===============
    # === HELPERS ===
    # ===============

    def _get_icon_name(self) -> str:
        """
        Retorna el icono asociado
        al tipo de notificación.
        """

        icons = {
            NotificationType.SUCCESS: "fa5s.check-circle",
            NotificationType.ERROR: "fa5s.times-circle",
            NotificationType.INFO: "fa5s.info-circle",
        }

        return icons[self.notification_type]

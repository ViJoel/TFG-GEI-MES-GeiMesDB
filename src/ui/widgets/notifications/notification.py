import qtawesome as qta
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QSizePolicy,
    QWidget,
)

from ui.utils.layouts import hbox
from ui.widgets.notifications.notification_type import NotificationType


class Notification(QWidget):
    """
    Widget flotante utilizado para mostrar
    mensajes breves al usuario.

    Responsabilidades:
    - Mostrar mensajes de estado.
    - Representar distintos tipos de notificación.
    - Permitir cerrar manualmente la notificación.
    """

    # =================
    # === VARIABLES ===
    # =================

    close_requested = Signal()

    # ============
    # === INIT ===
    # ============

    def __init__(
        self,
        notification_type: NotificationType,
        message: str,
        duration_ms: int | None = None,
    ) -> None:
        """
        Inicializa una nueva notificación.

        Args:
            notification_type (NotificationType):
                Tipo de notificación a mostrar.

            message (str):
                Texto principal de la notificación.

            duration_ms (int | None):
                Tiempo que permanecerá visible la
                notificación antes de cerrarse
                automáticamente.

                Si es ``None``, se utilizará la
                duración predeterminada definida
                para el tipo de notificación.

        """

        super().__init__()

        self.notification_type = notification_type

        self.message = message

        self.duration_ms = duration_ms

        # Ventana flotante sin bordes nativos.
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.ToolTip)

        self._set_type_property()

        self._setup_ui()

        self._connect_signals()

    # ================
    # === UI SETUP ===
    # ================

    def _setup_ui(
        self,
    ) -> None:
        """
        Construye la interfaz visual
        de la notificación.
        """

        # Layout horizontal principal.
        main_layout = hbox()

        self.setLayout(main_layout)

        # Limitar crecimiento excesivo del widget.
        self.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Fixed,
        )

        # Icono.
        icon_label = QLabel()

        icon_label.setPixmap(
            qta.icon(
                self._get_icon_name(),
            ).pixmap(18, 18)
        )

        # Texto.
        message_label = QLabel(f"[{self.notification_type.value}] {self.message}")

        # Botón de cierre.
        self.close_button = QPushButton()

        self.close_button.setIcon(qta.icon("fa5s.times"))

        main_layout.setContentsMargins(12, 8, 12, 8)
        main_layout.setSpacing(8)

        main_layout.addWidget(icon_label)
        main_layout.addWidget(message_label)
        main_layout.addSpacing(8)
        main_layout.addWidget(self.close_button)

    # ==================
    # === UI HELPERS ===
    # ==================

    def _get_icon_name(
        self,
    ) -> str:
        """
        Retorna el identificador del icono
        asociado al tipo de notificación.

        Returns:
            str:
                Nombre del icono compatible
                con QtAwesome.
        """

        icons = {
            NotificationType.SUCCESS: "fa5s.check-circle",
            NotificationType.ERROR: "fa5s.times-circle",
            NotificationType.INFO: "fa5s.info-circle",
        }

        return icons[self.notification_type]

    def _set_type_property(
        self,
    ) -> None:
        """
        Asigna la propiedad Qt 'type' basada en NotificationType.
        Usada para estilizado con QSS.
        """

        mapping = {
            NotificationType.SUCCESS: "success",
            NotificationType.ERROR: "error",
            NotificationType.INFO: "info",
        }

        self.setProperty("type", mapping[self.notification_type])

        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

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

        self.close_button.clicked.connect(self._request_close)

    def _request_close(
        self,
    ) -> None:
        """
        Solicita el cierre de la notificación.
        Punto único de entrada para cierre manual.
        """

        self.close_requested.emit()

    # ===================
    # === PRIVATE API ===
    # ===================

    def _get_duration(
        self,
    ) -> int:
        """
        Retorna la duración de visualización
        de la notificación.

        Si existe una duración personalizada,
        esta tiene prioridad sobre la duración
        predeterminada.

        Duraciones por defecto:
            - SUCCESS: 3000 ms
            - INFO: 3000 ms
            - ERROR: 3000 ms

        Returns:
            int:
                Duración en milisegundos.
        """

        if self.duration_ms is not None:
            return self.duration_ms

        return {
            NotificationType.SUCCESS: 3000,
            NotificationType.INFO: 3000,
            NotificationType.ERROR: 3000,
        }[self.notification_type]

    # ==================
    # === PUBLIC API ===
    # ==================

    def start_timer(
        self,
    ) -> None:
        """
        Inicia el temporizador de cierre
        automático.
        """

        QTimer.singleShot(self._get_duration(), self._request_close)

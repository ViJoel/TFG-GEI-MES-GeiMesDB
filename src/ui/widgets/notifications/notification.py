"""
Widget visual reutilizable para mostrar notificaciones
temporales dentro de la interfaz.

Permite representar mensajes informativos, de éxito
o error mediante iconografía y estilos consistentes.

Clases:
    - Notification
"""

import qtawesome as qta
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QSizePolicy,
    QWidget,
)

from ui.utils.layouts import hbox
from ui.widgets.notifications.notifications_type import NotificationType


class Notification(QWidget):
    """
    Widget flotante utilizado para mostrar
    mensajes breves al usuario.

    Responsabilidades:
    - Mostrar mensajes de estado.
    - Representar distintos tipos de notificación.
    - Permitir cerrar manualmente la notificación.
    """

    # ============
    # === INIT ===
    # ============

    def __init__(
        self,
        notification_type: NotificationType,
        message: str,
        parent=None,
        duration_ms: int | None = None,
    ):
        """
        Inicializa una nueva notificación.

        Args:
            notification_type (NotificationType):
                Tipo de notificación a mostrar.

            message (str):
                Texto principal de la notificación.

            parent:
                Widget padre de la notificación.

            duration_ms (int | None):
                Tiempo que permanecerá visible la
                notificación antes de cerrarse
                automáticamente.

                Si es ``None``, se utilizará la
                duración predeterminada definida
                para el tipo de notificación.

        """

        super().__init__(parent)

        self.notification_type = notification_type

        self.message = message

        self.duration_ms = duration_ms

        # Ventana flotante sin bordes nativos.
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.ToolTip)

        self._setup_ui()

    # ================
    # === UI SETUP ===
    # ================

    def _setup_ui(self) -> None:
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
        close_button = QPushButton()

        close_button.setIcon(qta.icon("fa5s.times"))

        close_button.clicked.connect(self.close)

        main_layout.setContentsMargins(12, 8, 12, 8)
        main_layout.setSpacing(8)

        main_layout.addWidget(icon_label)
        main_layout.addWidget(message_label)
        main_layout.addSpacing(8)
        main_layout.addWidget(close_button)

    def showEvent(self, event: QShowEvent) -> None:
        """
        Posiciona la notificación respecto
        a la ventana principal al mostrarse.

        La posición se calcula utilizando
        coordenadas globales para garantizar
        compatibilidad con ventanas flotantes
        (`Qt.ToolTip`) y distintos entornos
        de escritorio.
        """

        super().showEvent(event)

        parent = self.parentWidget()

        if parent is None:
            return

        margin = 16

        # Coordenadas globales reales de la ventana
        global_pos = parent.mapToGlobal(parent.rect().topLeft())

        self.move(
            global_pos.x() + margin,
            global_pos.y() + margin,
        )

        QTimer.singleShot(self._get_duration(), self.close)

    # ===============
    # === HELPERS ===
    # ===============

    def _get_icon_name(self) -> str:
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

    def _get_duration(self) -> int:
        """
        Retorna la duración, en milisegundos, durante la cual
        la notificación permanecerá visible antes de cerrarse
        automáticamente.

        Si se ha especificado una duración personalizada mediante
        ``duration_ms``, esta tendrá prioridad sobre los valores
        predeterminados asociados al tipo de notificación.

        Duraciones por defecto:
            - SUCCESS: 5000 ms
            - INFO: 5000 ms
            - ERROR: 10000 ms

        Returns:
            int:
                Tiempo de visualización de la notificación
                expresado en milisegundos.
        """

        if self.duration_ms is not None:
            return self.duration_ms

        return {
            NotificationType.SUCCESS: 5000,
            NotificationType.INFO: 5000,
            NotificationType.ERROR: 10000,
        }[self.notification_type]

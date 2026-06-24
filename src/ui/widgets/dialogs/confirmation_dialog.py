from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QPushButton,
    QWidget,
)

from ui.utils.layouts import hbox, vbox


class ConfirmationDialog(QDialog):
    """
    Diálogo reutilizable para solicitar confirmación
    antes de ejecutar una acción.

    Responsabilidades:
    - Mostrar un mensaje configurable.
    - Permitir confirmar o cancelar la operación.
    - Emitir señales explícitas según la decisión
      tomada por el usuario.
    """

    # Señales emitidas por el diálogo.
    confirmed = Signal()
    cancelled = Signal()

    # ============
    # === INIT ===
    # ============

    def __init__(
        self,
        title: str,
        message: str,
        parent=None,
    ) -> None:
        """
        Inicializa el diálogo de confirmación.

        Args:
            title (str):
                Título de la ventana.

            message (str):
                Mensaje principal mostrado al usuario.

            parent:
                Widget padre del diálogo.
        """

        super().__init__(parent.window())

        self.origin_widget = parent

        self.setObjectName("confirmation_dialog")

        self.setWindowTitle(title)

        # Bloquear interacción con la ventana padre
        # mientras el diálogo permanezca abierto.
        self.setModal(True)

        self._setup_ui(message)
        self._set_style()
        self._connect_signals()

    # ================
    # === UI SETUP ===
    # ================

    def _setup_ui(
        self,
        message: str,
    ) -> None:
        """
        Construye la interfaz visual del diálogo.

        Args:
            message (str):
                Texto principal mostrado al usuario.
        """

        main_layout = vbox()
        self.setLayout(main_layout)

        # Overlay que ocupa toda la ventana
        overlay = QWidget()
        overlay.setObjectName("dialog_overlay")

        main_layout.addWidget(overlay)

        overlay_layout = vbox()
        overlay.setLayout(overlay_layout)

        overlay_layout.addStretch()

        # Caja del diálogo
        container = QWidget()
        container.setObjectName("dialog_container")
        container.setFixedWidth(400)

        overlay_layout.addWidget(
            container,
            alignment=Qt.AlignmentFlag.AlignCenter,
        )

        overlay_layout.addStretch()

        # Layout interno del diálogo
        container_layout = vbox(
            ml=24,
            mt=24,
            mr=24,
            mb=24,
            sp=24,
        )
        container.setLayout(container_layout)

        # Mensaje
        self.message_label = QLabel(message)

        container_layout.addWidget(self.message_label)

        # Botones
        buttons_layout = hbox()

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setProperty("type", "primary")

        self.accept_button = QPushButton("Accept")
        self.accept_button.setProperty("type", "danger")

        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.accept_button)

        container_layout.addLayout(buttons_layout)

    def _set_style(self):
        """
        Establece parámetros visuales
        """

        self.setWindowFlags(Qt.FramelessWindowHint)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setGeometry(self.parent().rect())

        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    # ===============
    # === SIGNALS ===
    # ===============

    def _connect_signals(
        self,
    ) -> None:
        """
        Conecta señales de los widgets
        con sus handlers correspondientes.
        """

        self.accept_button.clicked.connect(
            self._on_accept_clicked,
        )

        self.cancel_button.clicked.connect(
            self._on_cancel_clicked,
        )

    # ======================
    # === EVENT HANDLERS ===
    # ======================

    def _on_accept_clicked(
        self,
    ) -> None:
        """
        Maneja la confirmación de la acción.
        """

        self.confirmed.emit()
        self.accept()

    def _on_cancel_clicked(
        self,
    ) -> None:
        """
        Maneja la cancelación de la acción.
        """

        self.cancelled.emit()
        self.reject()

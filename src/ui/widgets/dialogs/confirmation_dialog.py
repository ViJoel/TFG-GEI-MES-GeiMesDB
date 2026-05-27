from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QPushButton,
)

from ui.utils.layouts import hbox, vbox


class ConfirmationDialog(QDialog):
    """
    Diálogo reutilizable para solicitar confirmación
    al usuario antes de ejecutar acciones sensibles.

    Responsabilidades:
        - Mostrar un mensaje configurable.
        - Permitir aceptar o cancelar la acción.
        - Emitir señales explícitas de confirmación o cancelación.
    """

    # Señales
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
    ):
        """
        Inicializa el diálogo de confirmación.

        Args:
            title (str):
                Título de la ventana.

            message (str):
                Mensaje mostrado al usuario.

            parent:
                Widget padre del diálogo.
        """

        super().__init__(parent)

        self.setWindowTitle(title)

        # Bloquea interacción con la ventana padre
        # hasta cerrar el diálogo.
        self.setModal(True)

        self._setup_ui(message)
        self._connect_signals()

    # ================
    # === UI SETUP ===
    # ================

    def _setup_ui(self, message: str) -> None:
        """
        Construye la interfaz del diálogo.

        Args:
            message (str):
                Texto principal mostrado al usuario.
        """

        main_layout = vbox()

        self.setLayout(main_layout)

        # Mensaje principal
        self.message_label = QLabel(message)

        main_layout.addWidget(self.message_label)

        # Botones de acción
        buttons_layout = hbox()

        self.cancel_button = QPushButton("Cancel")
        self.accept_button = QPushButton("Accept")

        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.accept_button)

        main_layout.addLayout(buttons_layout)

    # ===============
    # === SIGNALS ===
    # ===============

    def _connect_signals(self) -> None:
        """
        Conecta los botones del diálogo
        con sus callbacks.
        """

        self.accept_button.clicked.connect(self._on_accept_clicked)

        self.cancel_button.clicked.connect(self._on_cancel_clicked)

    # ======================
    # === EVENT HANDLERS ===
    # ======================

    def _on_accept_clicked(self) -> None:
        """
        Maneja la confirmación de la acción.
        """

        self.confirmed.emit()

        self.accept()

    def _on_cancel_clicked(self) -> None:
        """
        Maneja la cancelación de la acción.
        """

        self.cancelled.emit()

        self.reject()

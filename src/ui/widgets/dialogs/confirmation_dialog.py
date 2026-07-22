from PySide6.QtCore import (
    Qt,
    Signal,
)
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QPushButton,
    QSizePolicy,
    QTextEdit,
    QWidget,
)

from ui.utils.layouts import (
    hbox,
    vbox,
)


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

    # =================
    # === CONSTANTS ===
    # =================

    _DIALOG_WIDTH = 400
    _DIALOG_MARGIN = 24

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
        self._adjust_message_height()
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

        # Overlay que ocupa toda la ventana.
        overlay = QWidget()
        overlay.setObjectName("dialog_overlay")

        main_layout.addWidget(overlay)

        overlay_layout = vbox()
        overlay.setLayout(overlay_layout)

        overlay_layout.addStretch()

        # Caja del diálogo.
        container = QWidget()
        container.setObjectName("dialog_container")
        container.setFixedWidth(self._DIALOG_WIDTH)

        overlay_layout.addWidget(
            container,
            alignment=Qt.AlignmentFlag.AlignCenter,
        )

        overlay_layout.addStretch()

        # Layout interno.
        container_layout = vbox(
            ml=self._DIALOG_MARGIN,
            mt=self._DIALOG_MARGIN,
            mr=self._DIALOG_MARGIN,
            mb=self._DIALOG_MARGIN,
            sp=24,
        )
        container.setLayout(container_layout)

        # Mensaje.
        self.message_view = QTextEdit()

        # Establecer el texto del mensaje.
        self.message_view.setText(message)

        # Convertir el editor en un visor de texto.
        self.message_view.setReadOnly(True)

        # Eliminar el borde nativo del QTextEdit.
        self.message_view.setFrameStyle(QFrame.NoFrame)

        # Solo se mostrará texto plano.
        self.message_view.setAcceptRichText(False)

        # Ocultar las barras de desplazamiento.
        self.message_view.setVerticalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff,
        )
        self.message_view.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff,
        )

        # Eliminar el margen interno del documento para que
        # el cálculo de altura sea exacto.
        self.message_view.document().setDocumentMargin(0)

        # Eliminar los márgenes del widget y de su viewport.
        self.message_view.setContentsMargins(0, 0, 0, 0)
        self.message_view.setViewportMargins(0, 0, 0, 0)

        # El alto será fijado manualmente según el contenido.
        self.message_view.setSizePolicy(
            QSizePolicy.Preferred,
            QSizePolicy.Fixed,
        )

        # Evitar que el widget pueda recibir el foco.
        self.message_view.setFocusPolicy(
            Qt.FocusPolicy.NoFocus,
        )

        # Deshabilitar cualquier interacción con el texto
        # (selección, copia, etc.).
        self.message_view.setTextInteractionFlags(
            Qt.TextInteractionFlag.NoTextInteraction,
        )

        # Mantener el cursor del ratón como una flecha
        # en lugar del cursor de edición de texto.
        self.message_view.setCursor(
            Qt.CursorShape.ArrowCursor,
        )
        self.message_view.viewport().setCursor(
            Qt.CursorShape.ArrowCursor,
        )

        container_layout.addWidget(self.message_view)

        # Botones.
        buttons_layout = hbox()

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setProperty("type", "primary")

        self.accept_button = QPushButton("Accept")
        self.accept_button.setProperty("type", "danger")

        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.accept_button)

        container_layout.addLayout(buttons_layout)

    # ======================
    # === PRIVATE UTILS ===
    # ======================

    def _adjust_message_height(
        self,
    ) -> None:
        """
        Ajusta la altura del visor de texto
        al contenido mostrado.

        QTextEdit no adapta automáticamente su altura al
        contenido, por lo que se calcula manualmente la
        altura del documento para evitar barras de
        desplazamiento y que el diálogo crezca de forma
        natural.
        """

        # Ancho útil del documento descontando los
        # márgenes internos del diálogo.
        content_width = self._DIALOG_WIDTH - (self._DIALOG_MARGIN * 2)

        document = self.message_view.document()

        # Recalcular el layout del documento para el
        # ancho disponible.
        document.setTextWidth(content_width)
        document.adjustSize()

        # Ajustar la altura del visor exactamente a la
        # altura del documento.
        self.message_view.setFixedHeight(int(document.size().height()))

    def _set_style(
        self,
    ) -> None:
        """
        Establece parámetros visuales.
        """

        # Eliminar el marco nativo de la ventana para
        # dibujar un diálogo completamente personalizado.
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint,
        )

        # Permitir que las zonas sin pintar del diálogo
        # sean transparentes (necesario para el overlay).
        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground,
        )

        # Hacer que el diálogo ocupe exactamente el área
        # de la ventana padre para cubrirla con el overlay.
        self.setGeometry(
            self.parent().rect(),
        )

        # Centrar el texto mostrado en el visor.
        self.message_view.setAlignment(
            Qt.AlignmentFlag.AlignCenter,
        )

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

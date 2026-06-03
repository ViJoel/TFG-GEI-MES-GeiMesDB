"""
Pantalla principal mostrada al iniciar
la aplicación.

Incluye un logo central y un mensaje
de bienvenida simple.

Clases:
    - Home
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QSizePolicy, QWidget

from common.constants import APP_NAME
from ui.utils.layouts import vbox
from ui.widgets.logos.app_logo import AppLogo


class Home(QWidget):
    """
    Pantalla principal inicial de la aplicación.

    Responsabilidades:
    - Mostrar branding básico.
    - Servir como pantalla de inicio.
    """

    # ============
    # === INIT ===
    # ============

    def __init__(self):
        """
        Inicializa la pantalla HOME.
        """

        super().__init__()

        self._setup_ui()

    # ================
    # === UI SETUP ===
    # ================

    def _setup_ui(self) -> None:
        """
        Construye la interfaz principal
        de la pantalla.
        """

        # Layout principal vertical.
        main_layout = vbox()

        self.setLayout(main_layout)

        # Permitir expansión completa.
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        # Espacio superior.
        main_layout.addStretch()

        # Logo principal.
        logo = AppLogo(size=300)

        main_layout.addWidget(
            logo,
            alignment=Qt.AlignmentFlag.AlignCenter,
        )

        main_layout.addSpacing(40)

        # Texto principal.
        title_label = QLabel(APP_NAME)

        title_label.setObjectName("homeTitle")

        main_layout.addWidget(
            title_label,
            alignment=Qt.AlignmentFlag.AlignCenter,
        )

        # Espacio inferior.
        main_layout.addStretch()

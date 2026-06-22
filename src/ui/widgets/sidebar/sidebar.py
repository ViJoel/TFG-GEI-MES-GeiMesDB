from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSizePolicy, QWidget

from ui.utils.layouts import vbox
from ui.widgets.logos.app_logo import AppLogo
from ui.widgets.sidebar.connections_list import ConnectionsList
from ui.widgets.sidebar.settings_button import SettingsButton


class Sidebar(QWidget):
    """
    Barra lateral principal de la aplicación.

    Responsabilidades:
    - Mostrar la identidad visual de la aplicación.
    - Alojar la lista de conexiones.
    - Proporcionar acceso a los ajustes globales.
    """

    # ============
    # === INIT ===
    # ============

    def __init__(
        self,
    ) -> None:
        """
        Inicializa el sidebar principal.
        """

        super().__init__()

        self.setObjectName("sidebar")

        self._setup_ui()

    # ================
    # === UI SETUP ===
    # ================

    def _setup_ui(
        self,
    ) -> None:
        """
        Construye la interfaz visual
        del sidebar.
        """

        self.setAttribute(Qt.WA_StyledBackground, True)

        # Configurar layout principal.
        self._setup_layout()

        # Logo de la aplicación.
        self.main_layout.addWidget(AppLogo())

        # Lista de conexiones persistidas.
        self.connections_list = ConnectionsList()

        self.main_layout.addWidget(self.connections_list)

        # Botón de ajustes globales.
        self.main_layout.addWidget(SettingsButton())

    def _setup_layout(
        self,
    ) -> None:
        """
        Configura el layout principal del sidebar.
        """

        # Crear layout vertical.
        self.main_layout = vbox()

        self.main_layout.setContentsMargins(12, 12, 12, 12)
        self.main_layout.setSpacing(16)

        # Asignar layout al widget.
        self.setLayout(self.main_layout)

        # Sidebar con altura expansible
        # y ancho fijo.
        self.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Expanding,
        )

        # Ancho fijo del sidebar.
        self.setFixedWidth(240)

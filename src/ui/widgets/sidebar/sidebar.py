from PySide6.QtWidgets import QSizePolicy, QWidget

from ui.utils.layouts import vbox
from ui.widgets.sidebar.app_logo import AppLogo
from ui.widgets.sidebar.connections_list import ConnectionsList
from ui.widgets.sidebar.settings_button import SettingsButton


class Sidebar(QWidget):

    # ============
    # === INIT ===
    # ============

    def __init__(self):
        super().__init__()

        self._setup_ui()

    # ================
    # === UI SETUP ===
    # ================

    def _setup_ui(self) -> None:
        """
        Configura la interfaz principal de la barra lateral.
        """

        # Barra lateral
        self._setup_layout()

        # Logo de la aplicación
        self.main_layout.addWidget(AppLogo())

        # Lista de conexiones
        self.main_layout.addWidget(ConnectionsList())

        # Botón de ajustes
        self.main_layout.addWidget(SettingsButton())

    def _setup_layout(self) -> None:
        """
        Configura el layout principal del sidebar.
        """

        # Crear layout vertical
        self.main_layout = vbox()

        # Asignar el layout al widget Sidebar
        self.setLayout(self.main_layout)

        # Sidebar vertical expansible
        self.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Expanding,
        )

        # Ancho fijo del sidebar
        self.setFixedWidth(200)

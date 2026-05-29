"""
Widget contenedor encargado de representar
la barra lateral principal de la aplicación.

El sidebar agrupa accesos y componentes
persistentes de navegación como:
- Logo de la aplicación.
- Lista de conexiones.
- Acceso a ajustes.

Clases:
    - Sidebar
"""

from PySide6.QtWidgets import QSizePolicy, QWidget

from ui.utils.layouts import vbox
from ui.widgets.sidebar.app_logo import AppLogo
from ui.widgets.sidebar.connections_list import ConnectionsList
from ui.widgets.sidebar.settings_button import SettingsButton


class Sidebar(QWidget):
    """
    Barra lateral principal utilizada
    como contenedor de navegación.

    Responsabilidades:
    - Mostrar branding de la aplicación.
    - Alojar la lista de conexiones.
    - Proporcionar acceso a ajustes globales.
    """

    # ============
    # === INIT ===
    # ============

    def __init__(self):
        """
        Inicializa el sidebar principal.
        """

        super().__init__()

        self._setup_ui()

    # ================
    # === UI SETUP ===
    # ================

    def _setup_ui(self) -> None:
        """
        Construye la interfaz visual
        del sidebar.
        """

        # Configurar layout principal.
        self._setup_layout()

        # Logo de la aplicación.
        self.main_layout.addWidget(AppLogo())

        # Lista de conexiones persistidas.
        self.connections_list = ConnectionsList()

        self.main_layout.addWidget(self.connections_list)

        # Botón de ajustes globales.
        self.main_layout.addWidget(SettingsButton())

    def _setup_layout(self) -> None:
        """
        Configura el layout principal del sidebar.
        """

        # Crear layout vertical.
        self.main_layout = vbox()

        # Asignar layout al widget.
        self.setLayout(self.main_layout)

        # Sidebar con altura expansible
        # y ancho fijo.
        self.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Expanding,
        )

        # Ancho fijo del sidebar.
        self.setFixedWidth(200)

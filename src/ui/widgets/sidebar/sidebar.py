from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QPushButton, QSizePolicy, QVBoxLayout, QWidget

from ui.common.paths import APP_LOGO
from ui.widgets.sidebar.app_logo import AppLogo
from ui.widgets.sidebar.connections_list import ConnectionsList
from ui.widgets.sidebar.settings_button import SettingsButton


class Sidebar(QWidget):
    def __init__(self):
        super().__init__()

        self._setup_ui()

    def _setup_ui(self):
        """
        Configura la interfaz principal de la barra lateral.
        """
        self._setup_layout()

        self.layout.addWidget(AppLogo())

        self.layout.addWidget(ConnectionsList())

        self.layout.addStretch()

        self.layout.addWidget(SettingsButton())

    def _setup_layout(self):
        """
        Configura el layout principal del sidebar.
        """

        # Crear layout vertical
        self.layout = QVBoxLayout()

        # Asignar el layout al widget Sidebar
        self.setLayout(self.layout)

        # Sidebar vertical expansible
        self.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Expanding,
        )

        # Ancho fijo del sidebar
        self.setFixedWidth(220)

        # Márgenes internos
        self.layout.setContentsMargins(10, 20, 10, 20)

        # Espaciado entre widgets
        self.layout.setSpacing(5)

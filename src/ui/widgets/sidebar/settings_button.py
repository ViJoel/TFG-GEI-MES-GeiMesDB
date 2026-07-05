from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QPushButton

from ui.common.paths import SETTINGS_ICON


class SettingsButton(QPushButton):
    """
    Botón lateral para acceder a la configuración
    de la aplicación.
    """

    def __init__(self):
        super().__init__()

        self.setObjectName("settings_button")

        self._setup_ui()

    def _setup_ui(self):
        """
        Configura la interfaz visual del botón.
        """

        # Icono del botón
        self.setIcon(QIcon(SETTINGS_ICON))

        # Tooltip informativo
        self.setToolTip("Configuración")

        # Cursor tipo mano
        self.setCursor(Qt.CursorShape.PointingHandCursor)

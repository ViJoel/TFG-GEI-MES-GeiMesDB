"""
Widget reutilizable encargado de representar
el logo principal de la aplicación.

El logo se carga desde disco y se escala
manteniendo la relación de aspecto original
para evitar deformaciones visuales.

Clases:
    - AppLogo
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel

from ui.common.paths import APP_LOGO


class AppLogo(QLabel):
    """
    Widget reutilizable para mostrar
    el logo principal de la aplicación.

    Responsabilidades:
    - Cargar el logo desde disco.
    - Escalar la imagen manteniendo proporciones.
    - Centrar visualmente el contenido.
    """

    # ============
    # === INIT ===
    # ============

    def __init__(self, size: int = 60):
        """
        Inicializa el widget del logo.

        Args:
            size (int):
                Tamaño máximo utilizado para
                escalar la imagen.
        """

        super().__init__()

        # Tamaño máximo del logo.
        self.size = size

        self._setup_ui()

    # ================
    # === UI SETUP ===
    # ================

    def _setup_ui(self):
        """
        Configura la interfaz visual
        del widget.
        """

        # Cargar imagen desde disco.
        pixmap = QPixmap(APP_LOGO)

        # Escalar imagen preservando
        # proporciones originales.
        scaled_pixmap = pixmap.scaled(
            self.size,
            self.size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        # Asignar imagen al QLabel.
        self.setPixmap(scaled_pixmap)

        # Centrar visualmente el contenido.
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

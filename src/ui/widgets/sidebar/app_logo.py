from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel

from ui.common.paths import APP_LOGO


class AppLogo(QLabel):
    """
    Widget reutilizable para mostrar el logo principal de la aplicación.

    El logo se carga desde disco utilizando la ruta definida en
    ``ui.common.paths.APP_LOGO`` y se escala manteniendo la
    relación de aspecto original.
    """

    def __init__(self, size: int = 60):
        """
        Inicializa el widget del logo.

        Args:
            size (int):
                Tamaño máximo (ancho y alto) utilizado para escalar
                la imagen del logo.
        """

        super().__init__()

        self.size = size

        self._setup_ui()

    def _setup_ui(self):
        """
        Configura el aspecto visual del widget.
        """

        # Cargar imagen desde disco
        pixmap = QPixmap(APP_LOGO)

        # Escalar imagen preservando proporciones
        scaled_pixmap = pixmap.scaled(
            self.size,
            self.size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        # Asignar imagen al QLabel
        self.setPixmap(scaled_pixmap)

        # Centrar contenido
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QSizePolicy


class Sidebar(QWidget):
    def __init__(self):
        super().__init__()

        self._setup_ui()

    def _setup_ui(self):
        self.sidebar()

        # Logo de la aplicación
        self.app_logo()

        # Lista de conexiones (placeholder por ahora)
        self.connections = QLabel("Connections")
        self.layout.addWidget(self.connections)

        # Botón añadir conexión
        self.add_button = QPushButton("+")
        self.layout.addWidget(self.add_button)

        # Espacio flexible (CLAVE)
        self.layout.addStretch()

        # Botón ajustes (abajo del todo)
        self.settings()

    def sidebar(self):
        # Layout vertical
        self.layout = QVBoxLayout(self)

        # Tamaño ajustable:
        # - Ancho mínimo
        # - Altura máxima
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)

        # Márgenes internos
        self.layout.setContentsMargins(10, 20, 10, 20)

        # Espaciado entre widgets
        self.layout.setSpacing(5)

    def app_logo(self):
        # QLabel para el logo
        self.logo = QLabel()
        self.logo.setAlignment(Qt.AlignCenter)

        # Cargar imagen
        pixmap = QPixmap("ui/resources/images/geimesdb_logo.png")

        # Escalar imagen
        pixmap = pixmap.scaled(
            60,  # Ancho
            60,  # Alto
            Qt.KeepAspectRatio,  # No se deforma
            Qt.SmoothTransformation,  # Mejor calidad
        )

        # Asignar imagen al label
        self.logo.setPixmap(pixmap)

        # Añadir al layout
        self.layout.addWidget(self.logo)

    def settings(self):
        self.icon = QLabel()
        self.icon.setAlignment(Qt.AlignCenter)

        # Cargar imagen
        pixmap = QPixmap("ui/resources/images/settings.png")

        # Escalar imagen
        pixmap = pixmap.scaled(
            30,  # Ancho
            30,  # Alto
            Qt.KeepAspectRatio,  # No se deforma
            Qt.SmoothTransformation,  # Mejor calidad
        )

        # Asignar imagen al label
        self.icon.setPixmap(pixmap)

        # Añadir al layout
        self.layout.addWidget(self.icon)

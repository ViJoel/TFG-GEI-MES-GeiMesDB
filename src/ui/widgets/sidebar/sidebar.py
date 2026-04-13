from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap


class Sidebar(QWidget):
    def __init__(self):
        super().__init__()

        self._setup_ui()

    def _setup_ui(self):
        self.sidebar()
        self.app_logo()

        # 2. Lista de conexiones (placeholder por ahora)
        self.connections = QLabel("Conexiones")
        self.layout.addWidget(self.connections)

        # 3. Botón añadir conexión
        self.add_button = QPushButton("+")
        self.layout.addWidget(self.add_button)

        # 🔥 4. Espacio flexible (CLAVE)
        self.layout.addStretch()

        # 5. Botón ajustes (abajo del todo)
        self.settings()

    def sidebar(self):
        self.layout = QVBoxLayout(self)  # Layout vertical
        self.setFixedWidth(70)  # Ancho fijo
        self.layout.setContentsMargins(0, 0, 0, 0)  # Quitar márgenes
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
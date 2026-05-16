from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QVBoxLayout, QWidget


from common.constants import APP_NAME
from ui.widgets.sidebar.sidebar import Sidebar


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        # Título de la ventana.
        self.setWindowTitle(APP_NAME)

        # Widget central obligatorio en QMainWindow.
        central = QWidget()
        self.setCentralWidget(central)

        # Layout principal (horizontal)
        layout = QHBoxLayout()
        central.setLayout(layout)

        # Sidebar
        sidebar = Sidebar()

        # Insertar sidebar en el layout
        layout.addWidget(sidebar)

        layout.addStretch()

    def _connect_signals(self):
        pass

    def retranslateUi(self):
        """Aquí irán TODOS los textos traducibles"""
        pass

    def changeEvent(self, event):
        if event.type() == QEvent.LanguageChange:
            self.retranslateUi()
        super().changeEvent(event)

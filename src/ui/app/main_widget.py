from ui.common.constants import APP_NAME
from ui.widgets.sidebar.sidebar import Sidebar
from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QWidget, QMainWindow, QHBoxLayout

class MainWidget(QMainWindow):
    def __init__(self):
        super().__init__()

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        self.setWindowTitle(APP_NAME)

        # Widget central obligatorio en QMainWindow
        central = QWidget()
        self.setCentralWidget(central)

        # Layout sobre el central widget
        self.layout = QHBoxLayout(central)

        # Widgets
        self.sidebar = Sidebar()
        self.main_area = QWidget()

        # Añadir widgets al layout
        self.layout.addWidget(self.sidebar)
        self.layout.addWidget(self.main_area)

        self.setMinimumSize(800, 600)

    def _connect_signals(self):
        pass

    def retranslateUi(self):
        """Aquí irán TODOS los textos traducibles"""
        pass

    def changeEvent(self, event):
        if event.type() == QEvent.LanguageChange:
            self.retranslateUi()
        super().changeEvent(event)

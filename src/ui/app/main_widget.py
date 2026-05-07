from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QVBoxLayout, QWidget

from common.constants import APP_NAME
from ui.widgets.sidebar.sidebar import Sidebar


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

        # Layout principal (horizontal)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar()

        # TreeView (placeholder)
        self.tree = QWidget()

        # Panel derecho
        self.right_panel = QWidget()
        right_layout = QVBoxLayout(self.right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Editor SQL
        self.editor = QWidget()

        # Resultados
        self.results = QWidget()

        right_layout.addWidget(self.editor, 1)
        right_layout.addWidget(self.results, 1)

        # Añadir todo al layout principal
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.tree, 1)
        main_layout.addWidget(self.right_panel, 2)

    def _connect_signals(self):
        pass

    def retranslateUi(self):
        """Aquí irán TODOS los textos traducibles"""
        pass

    def changeEvent(self, event):
        if event.type() == QEvent.LanguageChange:
            self.retranslateUi()
        super().changeEvent(event)

from PySide6.QtWidgets import QMainWindow, QWidget

from common.constants import APP_NAME
from ui.utils.layouts import hbox
from ui.widgets.forms.connection_form import ConnectionForm
from ui.widgets.sidebar.sidebar import Sidebar


class MainWindow(QMainWindow):

    # ============
    # === INIT ===
    # ============

    def __init__(self):
        super().__init__()

        self._setup_ui()

    # ================
    # === UI SETUP ===
    # ================

    def _setup_ui(self) -> None:
        # Título de la ventana.
        self.setWindowTitle(APP_NAME)

        # Widget central obligatorio en QMainWindow.
        central = QWidget()
        self.setCentralWidget(central)

        # Layout principal (horizontal)
        main_layout = hbox()
        central.setLayout(main_layout)

        # Sidebar
        sidebar = Sidebar()
        main_layout.addWidget(sidebar)

        main_layout.addStretch()

        main_layout.addWidget(ConnectionForm())

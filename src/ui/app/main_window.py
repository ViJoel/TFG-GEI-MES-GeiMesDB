from PySide6.QtWidgets import QLabel, QMainWindow, QStackedWidget, QWidget

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
        self._connect_signals()

    # ================
    # === UI SETUP ===
    # ================

    def _setup_ui(self) -> None:
        # Título de la ventana.
        self.setWindowTitle(APP_NAME)

        # Widget central (Obligatorio en QMainWindow).
        central = QWidget()
        self.setCentralWidget(central)

        # Layout principal
        main_layout = hbox()
        central.setLayout(main_layout)

        # Sidebar
        self.sidebar = Sidebar()
        main_layout.addWidget(self.sidebar)

        # Stack de pantallas
        self.stack = QStackedWidget()

        # Pantalla temporal (placeholder)
        self.home_page = QLabel("HOME")

        # Formulario de conexión
        self.connection_form = ConnectionForm()

        # Añadir páginas al stack
        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.connection_form)

        # Mostrar HOME al arrancar
        self.stack.setCurrentWidget(self.home_page)

        # Añadir stack al layout
        main_layout.addWidget(self.stack)

    # ===============
    # === SIGNALS ===
    # ===============

    def _connect_signals(self) -> None:
        self.sidebar.connections_list.add_connection_requested.connect(
            self._show_connection_form
        )

        self.connection_form.connection_saved.connect(self._on_connection_saved)

    # ======================
    # === EVENT HANDLERS ===
    # ======================

    def _on_connection_saved(self) -> None:

        # Recargar sidebar
        self.sidebar.connections_list.reload_connections()

        # Volver al home
        self.stack.setCurrentWidget(self.home_page)

    # ================
    # === UI STATE ===
    # ================

    def _show_connection_form(self) -> None:
        self.stack.setCurrentWidget(self.connection_form)

import logging

from PySide6.QtWidgets import QLabel, QMainWindow, QStackedWidget, QWidget

from common.constants import APP_NAME
from entities.connection import Connection
from modules.sessions.service import close_session, has_session, open_session
from ui.utils.layouts import hbox
from ui.widgets.forms.connection_form import ConnectionForm
from ui.widgets.notifications.notification import Notification
from ui.widgets.notifications.notifications_type import NotificationType
from ui.widgets.sidebar.sidebar import Sidebar

logger = logging.getLogger(__name__)


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

        self.sidebar.connections_list.edit_connection_requested.connect(
            self._show_edit_connection_form
        )

        self.connection_form.cancel_requested.connect(self._show_home_page)

        self.sidebar.connections_list.connection_open_requested.connect(
            self._open_connection_session
        )

        self.sidebar.connections_list.connection_close_requested.connect(
            self._close_connection_session
        )

    # ======================
    # === EVENT HANDLERS ===
    # ======================

    def _on_connection_saved(self) -> None:

        # Recargar sidebar
        self.sidebar.connections_list.reload_connections()

        # Volver al home
        self.stack.setCurrentWidget(self.home_page)

    def _open_connection_session(
        self,
        connection: Connection,
    ) -> None:

        try:

            open_session(connection)

            notification = Notification(
                NotificationType.SUCCESS,
                "Connection opened",
                parent=self,
            )

            notification.show()

            self.sidebar.connections_list.reload_connections()

        except Exception as e:

            logger.error(f"Error opening session: {e}")

            notification = Notification(
                NotificationType.ERROR,
                "Connection failed",
                parent=self,
            )

            notification.show()

    def _close_connection_session(
        self,
        connection: Connection,
    ) -> None:

        try:

            close_session(connection.id)

            notification = Notification(
                NotificationType.SUCCESS,
                "Connection closed",
                parent=self,
            )

            notification.show()

            self.sidebar.connections_list.reload_connections()

        except Exception as e:

            logger.error(f"Error closing session: {e}")

            notification = Notification(
                NotificationType.ERROR,
                "Error disconnecting",
                parent=self,
            )

            notification.show()

    # ================
    # === UI STATE ===
    # ================

    def _show_home_page(self) -> None:
        self.stack.setCurrentWidget(self.home_page)

    def _show_connection_form(self) -> None:
        self.connection_form.clear_form()
        self.stack.setCurrentWidget(self.connection_form)

    def _show_edit_connection_form(
        self,
        connection: Connection,
    ) -> None:
        self.connection_form.load_connection(connection)
        self.stack.setCurrentWidget(self.connection_form)

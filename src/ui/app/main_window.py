"""
Ventana principal de la aplicación.

Responsabilidades:
- Construir la interfaz principal.
- Coordinar navegación entre pantallas.
- Orquestar eventos globales de UI.
- Gestionar sesiones runtime de conexiones.
"""

import logging

from PySide6.QtWidgets import QLabel, QMainWindow, QStackedWidget, QWidget

from common.constants import APP_NAME
from entities.connection import Connection
from modules.sessions.service import close_session, open_session
from ui.utils.layouts import hbox
from ui.widgets.forms.connection_form import ConnectionForm
from ui.widgets.home.home import Home
from ui.widgets.notifications.notification import Notification
from ui.widgets.notifications.notifications_type import NotificationType
from ui.widgets.sidebar.sidebar import Sidebar

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """
    Ventana principal de la aplicación.

    Centraliza:
    - Navegación entre vistas,
    - Coordinación entre widgets,
    - Gestión de sesiones activas,
    - Eventos globales de interfaz.
    """

    # ============
    # === INIT ===
    # ============

    def __init__(self):
        """
        Inicializa la ventana principal.
        """

        super().__init__()

        self._setup_ui()
        self._connect_signals()

    # ================
    # === UI SETUP ===
    # ================

    def _setup_ui(self) -> None:
        """
        Construye la estructura visual principal
        de la aplicación.
        """

        # Título de la ventana.
        self.setWindowTitle(APP_NAME)

        # Widget central obligatorio en QMainWindow.
        central = QWidget()
        self.setCentralWidget(central)

        # Layout horizontal principal.
        main_layout = hbox()
        central.setLayout(main_layout)

        # Sidebar lateral.
        self.sidebar = Sidebar()
        main_layout.addWidget(self.sidebar)

        # Stack de navegación principal.
        self.stack = QStackedWidget()

        # Pantalla inicial.
        self.home_page = Home()

        # Formulario de conexiones.
        self.connection_form = ConnectionForm()

        # Registrar páginas.
        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.connection_form)

        # Mostrar pantalla inicial.
        self._show_home_page()

        # Añadir stack al layout principal.
        main_layout.addWidget(self.stack)

    # ===============
    # === SIGNALS ===
    # ===============

    def _connect_signals(self) -> None:
        """
        Conecta señales de widgets con sus
        correspondientes handlers.
        """

        # Navegación hacia creación de conexión.
        self.sidebar.connections_list.add_connection_requested.connect(
            self._show_connection_form
        )

        # Navegación hacia edición de conexión.
        self.sidebar.connections_list.edit_connection_requested.connect(
            self._show_edit_connection_form
        )

        # Retorno al home desde formulario.
        self.connection_form.cancel_requested.connect(self._show_home_page)

        # Evento de guardado exitoso.
        self.connection_form.connection_saved.connect(self._on_connection_saved)

        # Gestión runtime de sesiones.
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
        """
        Maneja el evento de guardado exitoso
        de una conexión.
        """

        # Refrescar sidebar.
        self.sidebar.connections_list.reload_connections()

        # Volver a la pantalla principal.
        self._show_home_page()

    def _open_connection_session(
        self,
        connection: Connection,
    ) -> None:
        """
        Abre una sesión runtime para la conexión
        especificada.

        Args:
            connection (Connection):
                Conexión persistida a abrir.
        """

        try:

            open_session(connection)

            notification = Notification(
                NotificationType.SUCCESS,
                "Connection opened",
                parent=self,
            )

            notification.show()

            # Refrescar estado visual.
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
        """
        Cierra la sesión runtime asociada
        a una conexión.

        Args:
            connection (Connection):
                Conexión asociada a la sesión.
        """

        try:

            close_session(connection.id)

            notification = Notification(
                NotificationType.SUCCESS,
                "Connection closed",
                parent=self,
            )

            notification.show()

            # Refrescar estado visual.
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
        """
        Navega hacia la pantalla principal.
        """

        self.stack.setCurrentWidget(self.home_page)

    def _show_connection_form(self) -> None:
        """
        Muestra el formulario de creación
        de conexiones.
        """

        self.connection_form.clear_form()

        self.stack.setCurrentWidget(self.connection_form)

    def _show_edit_connection_form(
        self,
        connection: Connection,
    ) -> None:
        """
        Muestra el formulario cargando una
        conexión existente.

        Args:
            connection (Connection):
                Conexión a editar.
        """

        self.connection_form.load_connection(connection)

        self.stack.setCurrentWidget(self.connection_form)

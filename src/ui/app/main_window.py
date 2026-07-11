"""
Componente responsable de la ventana principal
de la aplicación y de la coordinación global de
la interfaz de usuario.

Incluye la gestión de la navegación entre vistas
y del ciclo de vida de las sesiones activas.

Clases:
    - MainWindow
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QStackedWidget,
    QWidget,
)

from common.constants import APP_NAME
from entities.connection import Connection
from entities.message_type import MessageType
from log.app_logger import get_logger
from modules.sessions.service import (
    close_session,
    open_session,
)
from ui.app.app_actions import notify
from ui.app.app_context import AppContext
from ui.app.worker_error import WorkerError
from ui.utils.layouts import hbox
from ui.widgets.forms.connection_form import ConnectionForm
from ui.widgets.home.home import Home
from ui.widgets.sidebar.sidebar import Sidebar
from ui.widgets.workspace.workspace import Workspace

logger = get_logger(__name__)


class MainWindow(QMainWindow):
    """
    Ventana principal de la aplicación.

    Responsabilidades:
    - Construir la interfaz principal.
    - Coordinar la navegación entre vistas.
    - Gestionar las sesiones activas.
    - Atender eventos globales de la interfaz.
    """

    # ============
    # === INIT ===
    # ============

    def __init__(
        self,
    ):
        """
        Inicializa la ventana principal.
        """

        super().__init__()

        self._setup_ui()
        self._connect_signals()

    # ================
    # === UI SETUP ===
    # ================

    def _setup_ui(
        self,
    ) -> None:
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
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(6)

        central.setLayout(main_layout)

        # Sidebar lateral.
        self.sidebar = Sidebar()
        main_layout.addWidget(self.sidebar)

        # Stack de navegación principal.
        self.stack = QStackedWidget()

        # Pantalla inicial.
        self.home_page = Home()

        # Formulario de conexiones.
        self.connection_form_page = QWidget()
        connection_form_layout = hbox()
        connection_form_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.connection_form_page.setLayout(connection_form_layout)

        self.connection_form = ConnectionForm()

        connection_form_layout.addWidget(self.connection_form)

        # Espacio de trabajo
        self.workspaces: dict[str, Workspace] = {}

        # Registrar páginas.
        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.connection_form_page)

        # Mostrar pantalla inicial.
        self._show_home_page()

        # Añadir stack al layout principal.
        main_layout.addWidget(self.stack)

    # ================
    # === UI STATE ===
    # ================

    def _show_home_page(
        self,
    ) -> None:
        """
        Navega hacia la pantalla principal.
        """

        self.stack.setCurrentWidget(self.home_page)

    def _show_connection_form(
        self,
    ) -> None:
        """
        Muestra el formulario de creación
        de conexiones.
        """

        self.connection_form.clear_form()

        self.stack.setCurrentWidget(self.connection_form_page)

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

        self.stack.setCurrentWidget(self.connection_form_page)

    def _show_workspace(
        self,
        connection: Connection,
    ) -> None:
        """
        Muestra el espacio de trabajo asociado
        a la conexión indicada.

        Args:
            connection (Connection):
                Conexión cuyo espacio de trabajo
                debe mostrarse.
        """
        workspace = self.workspaces.get(connection.id)

        if workspace:
            self.stack.setCurrentWidget(workspace)

    # ===============
    # === SIGNALS ===
    # ===============

    def _connect_signals(
        self,
    ) -> None:
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

        self.sidebar.connections_list.connection_selected.connect(
            self._on_connection_selected
        )

    # ======================
    # === EVENT HANDLERS ===
    # ======================

    def _on_connection_saved(
        self,
    ) -> None:
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
        Abre una sesión runtime para la conexión especificada.

        Args:
            connection (Connection):
                Conexión sobre la que se abrirá la sesión.
        """

        notify(
            MessageType.WARNING,
            "Connecting...",
        )

        AppContext.get_task_manager().run(
            open_session,
            connection,
            on_success=lambda _: self._on_open_connection_session_success(connection),
            on_error=self._on_open_connection_session_error,
        )

    def _close_connection_session(
        self,
        connection: Connection,
    ) -> None:
        """
        Cierra la sesión runtime asociada a una
        conexión y elimina su espacio de trabajo.

        Args:
            connection (Connection):
                Conexión asociada a la sesión.
        """

        notify(
            MessageType.WARNING,
            "Disconnecting...",
        )

        AppContext.get_task_manager().run(
            close_session,
            connection.id,
            on_success=lambda _: self._on_close_connection_session_success(connection),
            on_error=self._on_close_connection_session_error,
        )

    def _on_connection_selected(
        self,
        connection: Connection,
    ) -> None:
        """
        Actualiza la vista activa según el estado
        de la conexión seleccionada.

        Si existe un espacio de trabajo asociado
        a la conexión, se muestra dicho espacio.
        En caso contrario se muestra la pantalla
        principal.

        Args:
            connection (Connection):
                Conexión seleccionada.
        """
        if connection.id in self.workspaces:
            self._show_workspace(connection)
        else:
            self._show_home_page()

    # =====================
    # === EVENT HELPERS ===
    # =====================

    def _on_open_connection_session_success(
        self,
        connection: Connection,
    ) -> None:

        notify(
            MessageType.SUCCESS,
            "Connected.",
        )

        if connection.id not in self.workspaces:

            workspace = Workspace(connection)
            self.workspaces[connection.id] = workspace
            self.stack.addWidget(workspace)

        self._show_workspace(connection)

        self.sidebar.connections_list.reload_connections()

    def _on_open_connection_session_error(
        self,
        error: WorkerError,
    ) -> None:

        logger.error(error.traceback)

        notify(
            MessageType.ERROR,
            "Connection failed.",
        )

    def _on_close_connection_session_success(
        self,
        connection: Connection,
    ) -> None:

        notify(
            MessageType.SUCCESS,
            "Disconnected.",
        )

        # Eliminar espacio de trabajo.
        workspace = self.workspaces.pop(connection.id, None)

        if workspace:
            self.stack.removeWidget(workspace)
            workspace.deleteLater()

        # Refrescar estado visual.
        self.sidebar.connections_list.reload_connections()

    def _on_close_connection_session_error(
        self,
        error: WorkerError,
    ) -> None:

        logger.error(error.traceback)

        notify(
            MessageType.ERROR,
            "Disconnection failed.",
        )

    # ====================
    # === QT OVERRIDES ===
    # ====================

    def moveEvent(self, event):
        """
        Reposiciona las notificaciones cuando
        la ventana principal cambia de posición.
        """

        super().moveEvent(event)

        AppContext.notification_manager.reposition()

    def resizeEvent(self, event):
        """
        Reposiciona las notificaciones cuando
        la ventana principal cambia de tamaño.
        """

        super().resizeEvent(event)

        AppContext.notification_manager.reposition()

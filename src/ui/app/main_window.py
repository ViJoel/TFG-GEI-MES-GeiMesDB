"""
Componente responsable de la ventana principal
de la aplicación y de la coordinación global de
la interfaz de usuario.

Incluye la gestión de la navegación entre vistas
y del ciclo de vida de las sesiones activas.

Clases:
    - MainWindow
"""

from PySide6.QtCore import (
    QCoreApplication,
    Qt,
)
from PySide6.QtGui import (
    QCloseEvent,
    QGuiApplication,
)
from PySide6.QtWidgets import (
    QMainWindow,
    QSizePolicy,
    QStackedWidget,
    QWidget,
)

from common.constants import APP_NAME
from entities.connection import Connection
from entities.message_type import MessageType
from entities.unsaved_changes_count import UnsavedChangesCount
from log.app_logger import get_logger
from modules.sessions.service import (
    close_session,
    open_session,
)
from ui.app.app_actions import notify
from ui.app.app_context import AppContext
from ui.app.worker_error import WorkerError
from ui.utils.layouts import hbox
from ui.widgets.dialogs.confirmation_dialog import ConfirmationDialog
from ui.widgets.forms.connection_form import ConnectionForm
from ui.widgets.home.home import Home
from ui.widgets.settings.settings_menu import SettingsMenu
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

    # =================
    # === VARIABLES ===
    # =================
    _was_maximized: bool = False

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

        self._last_page: QWidget | None = None

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

        # Definir un tamaño mínimo razonable para
        # permitir acoples en mitades de pantalla.
        self.setMinimumSize(600, 400)

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
        # Permitir que el QStackedWidget se expanda
        # libremente en ambas direcciones.
        self.stack.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        # Pantalla inicial.
        self.home_page = Home()

        # Formulario de conexiones.
        self.connection_form_page = QWidget()
        connection_form_layout = hbox()
        connection_form_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.connection_form_page.setLayout(connection_form_layout)

        self.connection_form = ConnectionForm()

        connection_form_layout.addWidget(self.connection_form)

        # Menú de ajustes.
        self.settings_menu_page = QWidget()
        settings_menu_layout = hbox()
        settings_menu_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.settings_menu_page.setLayout(settings_menu_layout)

        self.settings_menu = SettingsMenu()

        settings_menu_layout.addWidget(self.settings_menu)

        # Espacios de trabajo.
        self.workspaces: dict[str, Workspace] = {}

        # Registrar páginas.
        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.connection_form_page)
        self.stack.addWidget(self.settings_menu_page)

        # Mostrar pantalla inicial.
        self._show_home_page()

        # Añadir stack al layout principal.
        main_layout.addWidget(self.stack)

    # ================
    # === UI STATE ===
    # ================

    def _show_page(
        self,
        page: QWidget,
        return_to: QWidget | None = None,
    ) -> None:
        """
        Muestra la página indicada y, opcionalmente,
        registra la página a la que debe regresar
        posteriormente.

        Args:
            page (QWidget):
                Página que debe mostrarse.

            return_to (QWidget | None):
                Página que se utilizará como destino
                al regresar desde la vista actual.

                Si es `None`, se conserva la página
                de retorno previamente registrada.
        """

        if return_to is not None:
            self._last_page = return_to

        self.stack.setCurrentWidget(page)

    def _show_last_page(
        self,
    ) -> None:
        """
        Muestra la última página registrada como
        destino de retorno.

        Si no existe ninguna página registrada,
        se muestra la pantalla principal.
        """

        self.stack.setCurrentWidget(
            self._last_page or self.home_page,
        )

    def _show_home_page(
        self,
    ) -> None:
        """
        Navega hacia la pantalla principal.
        """

        self._show_page(
            page=self.home_page,
            return_to=self.home_page,
        )

    def _show_connection_form(
        self,
    ) -> None:
        """
        Muestra el formulario de creación
        de conexiones.
        """

        self.connection_form.clear_form()

        self._show_page(
            page=self.connection_form_page,
        )

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

        self._show_page(
            page=self.connection_form_page,
            return_to=self.home_page,
        )

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
            self._show_page(
                page=workspace,
                return_to=workspace,
            )

    def _show_settings_menu(
        self,
    ) -> None:
        """
        Muestra el menú de ajustes.
        """

        self._show_page(
            page=self.settings_menu_page,
        )

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
        self.connection_form.cancel_requested.connect(self._show_last_page)

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

        # Navegación hacia el menú de ajustes
        self.sidebar.settings_button.clicked.connect(
            self._show_settings_menu,
        )

        # Retorno desde el menú de ajustes.
        self.settings_menu.cancel_button.clicked.connect(
            self._show_last_page,
        )

        self.settings_menu.accept_button.clicked.connect(
            self._show_last_page,
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

        # Volver explícitamente al Home.
        self._show_home_page()

        # Refrescar estado visual del sidebar.
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

    def moveEvent(
        self,
        event,
    ) -> None:
        """
        Reposiciona las notificaciones cuando
        la ventana principal cambia de posición.
        """

        super().moveEvent(event)

        AppContext.notification_manager.reposition()

    def resizeEvent(
        self,
        event,
    ) -> None:
        """
        Reposiciona las notificaciones cuando
        la ventana principal cambia de tamaño.
        """

        super().resizeEvent(event)

        AppContext.notification_manager.reposition()

    def keyPressEvent(
        self,
        event,
    ) -> None:
        """
        Maneja los eventos de teclado de la ventana.

        Intercepta de manera específica la tecla F11 para
        alternar el modo de pantalla completa. Asegura que la
        transición respete el monitor activo actual basándose
        en el centro geométrico de la ventana, y restaura
        el estado previo (maximizado o normal) al salir.

        Args:
            event (QKeyEvent):
                Evento de teclado enviado por el sistema
                que contiene la tecla presionada.
        """

        if event.key() == Qt.Key.Key_F11:
            if self.isFullScreen():
                # Restauramos al estado previo.
                if self._was_maximized:
                    self.showMaximized()  # Modo ventana maximizado.
                else:
                    self.showNormal()  # Modo ventana sin maximizar.
            else:
                # 1. Guardamos el estado actual.
                self._was_maximized = self.isMaximized()

                # 2. Aseguramos la existencia del
                # handle de la ventana nativa.
                if not self.windowHandle():
                    self.createWinId()

                # 3. Detectamos la pantalla basándonos
                # en el centro geométrico de la ventana.
                window_center = self.frameGeometry().center()
                target_screen = QGuiApplication.screenAt(window_center) or self.screen()

                # 4. Asignamos la pantalla al handle nativo.
                if target_screen and self.windowHandle():
                    self.windowHandle().setScreen(target_screen)
                    # Procesamos eventos pendientes para
                    # que el Servidor X/Windows registre
                    # la reubicación de pantalla antes
                    # del resize.
                    QCoreApplication.processEvents()

                # 5. Activamos pantalla completa.
                self.showFullScreen()
        else:
            # Importante: pasa otros eventos de
            # teclado al comportamiento por defecto.
            super().keyPressEvent(event)

    def closeEvent(
        self,
        event: QCloseEvent,
    ) -> None:
        """
        Maneja el intento de cierre de la ventana principal.

        Comprueba si existen cambios sin guardar en los espacios
        de trabajo activos y solicita confirmación al usuario
        antes de cerrar la aplicación.

        Args:
            event (QCloseEvent):
                Evento de cierre de Qt.
        """

        # 1. Recopilar cambios sin guardar en todos los workspaces activos.
        unsaved_items: list[UnsavedChangesCount] = []
        for workspace in self.workspaces.values():
            changes = workspace.get_unsaved_changes_count()
            if changes:
                unsaved_items.append(changes)

        # 2. Si hay cambios pendientes, mostrar el diálogo de confirmación.
        if unsaved_items:
            # Construir un resumen con los nombres de las conexiones y sus archivos.
            details_html = "<br>".join(
                [
                    f"• <b>{item.connection_name}</b>: {item.unsaved_changes} file(s)"
                    for item in unsaved_items
                ]
            )

            dialog = ConfirmationDialog(
                title="Exit application",
                message=(
                    "⚠️ <b>Discard unsaved changes?</b> ⚠️<br><br>"
                    "You have unsaved changes in the following workspace(s):<br>"
                    f"{details_html}<br><br>"
                    "If you exit now, all unsaved changes will be lost.<br>"
                    "This action can not be undone."
                ),
                parent=self,
            )

            # Si el usuario cancela o cierra el diálogo, abortar el cierre.
            if not dialog.exec():
                event.ignore()
                return

        # 3. Si no hay cambios o el usuario confirmó, permitir el cierre.
        event.accept()

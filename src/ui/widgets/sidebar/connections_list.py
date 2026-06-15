import logging

import qtawesome as qta
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QIcon
from PySide6.QtWidgets import (
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QWidget,
)

from entities.connection import Connection
from entities.driver import Driver
from modules.connections.service import delete_connection, get_connections
from modules.sessions.service import has_session
from ui.common.paths import MYSQL_LOGO, ORACLE_LOGO, POSTGRESQL_LOGO, SQLITE_LOGO
from ui.state.state import set_selected_connection
from ui.utils.layouts import hbox, vbox
from ui.widgets.dialogs.confirmation_dialog import ConfirmationDialog
from ui.widgets.notifications.notification import Notification
from ui.widgets.notifications.notifications_type import NotificationType

logger = logging.getLogger(__name__)


class ConnectionsList(QWidget):
    """
    Widget encargado de visualizar y gestionar
    la lista de conexiones persistidas.

    Responsabilidades:
    - Mostrar las conexiones disponibles.
    - Gestionar la selección de conexiones.
    - Emitir eventos asociados a las acciones
      del usuario.
    - Reflejar el estado de las sesiones activas.
    """

    # =================
    # === VARIABLES ===
    # =================

    connection_selected = Signal(Connection)
    add_connection_requested = Signal()
    edit_connection_requested = Signal(Connection)
    connection_open_requested = Signal(Connection)
    connection_close_requested = Signal(Connection)

    # ============
    # === INIT ===
    # ============

    def __init__(
        self,
    ) -> None:
        """
        Inicializa la lista de conexiones.
        """

        super().__init__()

        self._setup_ui()
        self._connect_signals()
        self._load_connections()

    # ================
    # === UI SETUP ===
    # ================

    def _setup_ui(
        self,
    ) -> None:
        """
        Construye la interfaz principal
        del widget.
        """

        # Layout vertical principal.
        main_layout = vbox()

        self.setLayout(main_layout)

        # Barra de acciones.
        self._setup_buttons(main_layout)

        # Estado inicial de botones.
        self._setup_buttons_state()

        # Lista visual de conexiones.
        self._setup_connections_list(main_layout)

    def _setup_buttons(
        self,
        parent_layout,
    ) -> None:
        """
        Construye la barra de botones
        de acciones rápidas.

        Args:
            parent_layout:
                Layout padre donde se añadirá
                la barra de botones.
        """

        buttons_layout = hbox()

        # Botones
        self.add_button = self._create_icon_button("fa5s.plus")
        self.edit_button = self._create_icon_button("fa5s.edit")
        self.delete_button = self._create_icon_button("fa5s.trash")
        self.connect_button = self._create_icon_button("mdi.wifi")
        self.disconnect_button = self._create_icon_button("mdi.wifi-off")

        # Añadir botones al layout
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.edit_button)
        buttons_layout.addWidget(self.delete_button)
        buttons_layout.addWidget(self.connect_button)
        buttons_layout.addWidget(self.disconnect_button)

        parent_layout.addLayout(buttons_layout)

    def _setup_connections_list(
        self,
        parent_layout,
    ) -> None:
        """
        Construye la lista visual
        de conexiones.

        Args:
            parent_layout:
                Layout padre donde se añadirá
                la lista.
        """

        self.list_widget = QListWidget()

        # Permitir expansión vertical y horizontal.
        self.list_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        parent_layout.addWidget(self.list_widget)

    # ================
    # === UI STATE ===
    # ================

    def _setup_buttons_state(
        self,
    ) -> None:
        """
        Configura el estado inicial de los botones.
        """

        self.add_button.setEnabled(True)
        self.edit_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        self.connect_button.setEnabled(False)
        self.disconnect_button.setEnabled(False)

    def _update_buttons_state(
        self,
        connection: Connection | None,
    ) -> None:
        """
        Actualiza el estado visual
        de los botones según la conexión
        seleccionada y el estado de sesión.

        Args:
            connection (Connection | None):
                Conexión actualmente seleccionada.
        """

        has_selection = connection is not None

        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)

        if not has_selection:
            self.connect_button.setEnabled(False)
            self.disconnect_button.setEnabled(False)
            return

        is_connected = has_session(connection.id)

        self.connect_button.setEnabled(not is_connected)
        self.disconnect_button.setEnabled(is_connected)

    def _clear_selection(
        self,
    ) -> None:
        """
        Limpia la selección actual de la lista.
        """

        self.list_widget.clearSelection()
        self.list_widget.setCurrentItem(None)

        set_selected_connection(None)

    # ==================
    # === UI HELPERS ===
    # ==================

    def _create_icon_button(
        self,
        icon_name: str,
    ) -> QPushButton:
        """
        Crea un botón cuadrado basado
        únicamente en iconografía.

        Args:
            icon_name (str):
                Nombre del icono compatible
                con QtAwesome.

        Returns:
            QPushButton:
                Botón configurado.
        """

        button = QPushButton()
        button.setIcon(qta.icon(icon_name))
        button.setFixedSize(32, 32)
        return button

    def _get_driver_icon(
        self,
        driver: Driver,
    ) -> QIcon:
        """
        Retorna el icono asociado
        al driver de base de datos.

        Args:
            driver (Driver):
                Driver de la conexión.

        Returns:
            QIcon:
                Icono correspondiente.
        """

        icons = {
            Driver.POSTGRESQL: QIcon(POSTGRESQL_LOGO),
            Driver.MYSQL: QIcon(MYSQL_LOGO),
            Driver.SQLITE: QIcon(SQLITE_LOGO),
            Driver.ORACLE: QIcon(ORACLE_LOGO),
        }

        return icons.get(driver, QIcon())

    def _add_connection_item(
        self,
        connection: Connection,
    ) -> None:
        """
        Añade una conexión individual a la lista visual.

        Args:
            connection (Connection):
                Conexión a representar.
        """

        # Texto visible.
        connection_name = connection.name or "Sin nombre"

        item = QListWidgetItem(connection_name)

        # Icono según driver.
        item.setIcon(self._get_driver_icon(connection.driver))

        # Resaltar conexiones con sesión activa.
        if has_session(connection.id):
            item.setBackground(QColor("green"))

        # Guardar objeto completo dentro del item.
        item.setData(
            Qt.ItemDataRole.UserRole,
            connection,
        )

        self.list_widget.addItem(item)

    # ===============
    # === SIGNALS ===
    # ===============

    def _connect_signals(
        self,
    ) -> None:
        """
        Conecta señales de widgets
        con sus handlers correspondientes.
        """

        # Selección de elementos.
        self.list_widget.itemSelectionChanged.connect(self._on_selection_changed)

        # Acciones CRUD.
        self.add_button.clicked.connect(self._on_add_button_clicked)
        self.edit_button.clicked.connect(self._on_edit_button_clicked)
        self.delete_button.clicked.connect(self._on_delete_button_clicked)

        # Gestión de sesiones.
        self.connect_button.clicked.connect(self._on_connect_button_clicked)
        self.disconnect_button.clicked.connect(self._on_disconnect_button_clicked)

    # ======================
    # === EVENT HANDLERS ===
    # ======================

    def _on_selection_changed(
        self,
    ) -> None:
        """
        Maneja cambios de selección
        dentro de la lista.
        """

        connection = self._get_selected_connection()

        set_selected_connection(connection)

        self._update_buttons_state(connection)

        if connection is not None:
            logger.debug(
                f"Connection '{connection.name}' (ID: {connection.id}) selected."
            )
            self.connection_selected.emit(connection)
        else:
            logger.debug(f"Connection selected: {None}.")

    def _on_add_button_clicked(
        self,
    ) -> None:
        """
        Solicita apertura del formulario
        de creación de conexiones.
        """

        logger.info("Connection creation requested.")

        self.add_connection_requested.emit()

    def _on_delete_button_clicked(
        self,
    ) -> None:
        """
        Solicita confirmación para eliminar
        la conexión seleccionada.
        """

        connection = self._get_selected_connection()

        if connection is None:
            logger.warning("Delete attempted without selection.")
            return

        dialog = ConfirmationDialog(
            title="Delete connection",
            message=(f"Are you sure you want to delete '{connection.name}'?"),
            parent=self,
        )

        dialog.confirmed.connect(lambda: self._delete_connection(connection))

        dialog.exec()

    def _on_edit_button_clicked(
        self,
    ) -> None:
        """
        Solicita edición de la conexión
        seleccionada.
        """

        connection = self._get_selected_connection()

        if connection is None:
            return

        logger.info(
            f"Connection '{connection.name}' (ID: {connection.id}) edit requested."
        )

        self.connection_close_requested.emit(connection)

        self.edit_connection_requested.emit(connection)

    def _on_connect_button_clicked(
        self,
    ) -> None:
        """
        Solicita apertura de sesión
        para la conexión seleccionada.
        """

        connection = self._get_selected_connection()

        if connection is None:
            return

        logger.info(
            f"Session open requested for '{connection.name}' (ID: {connection.id})."
        )

        self.connection_open_requested.emit(connection)

    def _on_disconnect_button_clicked(
        self,
    ) -> None:
        """
        Solicita cierre de sesión
        para la conexión seleccionada.
        """

        connection = self._get_selected_connection()

        if connection is None:
            return

        logger.info(
            f"Session close requested for '{connection.name}' (ID: {connection.id})."
        )

        self.connection_close_requested.emit(connection)

    # =====================
    # === EVENT HELPERS ===
    # =====================

    def _delete_connection(
        self,
        connection: Connection,
    ) -> None:
        """
        Elimina una conexión persistida
        y actualiza la interfaz.

        Args:
            connection (Connection):
                Conexión a eliminar.
        """

        try:

            logger.info(
                f"Deleting connection '{connection.name}' (ID: {connection.id})..."
            )

            delete_connection(connection)

            logger.success(
                f"Connection '{connection.name}' (ID: {connection.id}) deleted."
            )

            Notification(
                NotificationType.SUCCESS,
                "Connection deleted",
                parent=self.window(),
            ).show()

            self.reload_connections()

            self._clear_selection()

        except Exception as e:

            logger.error(
                f"Failed to delete connection '{connection.name}' (ID: {connection.id}). "
                f"Exception: {e}"
            )

            Notification(
                NotificationType.ERROR,
                "Error deleting",
                parent=self.window(),
            ).show()

    def _load_connections(
        self,
    ) -> None:
        """
        Recupera las conexiones persistidas
        y reconstruye la lista visual
        preservando la selección actual.
        """

        selected_connection = self._get_selected_connection()

        selected_id = (
            selected_connection.id if selected_connection is not None else None
        )

        connections = get_connections()

        # Bloquear señales durante reconstrucción
        self.list_widget.blockSignals(True)

        self.list_widget.clear()

        restored_connection = None

        for connection in connections:

            self._add_connection_item(connection)

            if connection.id == selected_id:

                item = self.list_widget.item(self.list_widget.count() - 1)

                self.list_widget.setCurrentItem(item)

                restored_connection = connection

        # Reactivar señales
        self.list_widget.blockSignals(False)

        # Actualizar conexión seleccionada en el estado global
        set_selected_connection(restored_connection)

        # Actualizar estado manualmente
        self._update_buttons_state(restored_connection)

    # ===================
    # === PRIVATE API ===
    # ===================

    def _get_selected_connection(
        self,
    ) -> Connection | None:
        """
        Retorna la conexión actualmente seleccionada.

        Returns:
            Connection | None:
                Conexión seleccionada o `None`
                si no existe selección.
        """

        item = self.list_widget.currentItem()

        if item is None:
            return None

        return item.data(Qt.ItemDataRole.UserRole)

    # ==================
    # === PUBLIC API ===
    # ==================

    def reload_connections(
        self,
    ) -> None:
        """
        Recarga las conexiones persistidas
        y actualiza la lista visual.
        """

        logger.debug("Reloading connections list...")

        self._load_connections()

        logger.debug("Connections list reloaded.")

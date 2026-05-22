import logging

import qtawesome as qta
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QWidget,
)

from model.connections.connection import Connection
from model.connections.driver import Driver
from service.connections import get_connections
from ui.common.paths import MYSQL_LOGO, ORACLE_LOGO, POSTGRESQL_LOGO, SQLITE_LOGO
from ui.utils.layouts import hbox, vbox

# Crear sub-logger
logger = logging.getLogger(__name__)


class ConnectionsList(QWidget):
    """
    Widget encargado de visualizar y gestionar la lista de conexiones.
    """

    # Señal emitida al seleccionar una conexión
    connection_selected = Signal(Connection)

    # ============
    # === INIT ===
    # ============

    def __init__(self):
        super().__init__()

        self._setup_ui()
        self._connect_signals()
        self._load_connections()

    # ================
    # === UI SETUP ===
    # ================

    def _setup_ui(self) -> None:
        """
        Configura la interfaz del widget.
        """

        # Layout principal
        main_layout = vbox()
        self.setLayout(main_layout)

        # Botones
        self._setup_buttons(main_layout)
        self._setup_buttons_state()

        # Lista de conexiones
        self._setup_connections_list(main_layout)

    def _setup_buttons(self, parent_layout) -> None:
        # Layout horizontal
        buttons_layout = hbox()

        # Botones
        self.add_button = self._create_icon_button("fa5s.plus")
        self.edit_button = self._create_icon_button("fa5s.edit")
        self.delete_button = self._create_icon_button("fa5s.trash")
        self.connect_button = self._create_icon_button("mdi.wifi")
        self.disconnect_button = self._create_icon_button("mdi.wifi-off")

        # Añadir botones al layout horizontal
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.edit_button)
        buttons_layout.addWidget(self.delete_button)
        buttons_layout.addWidget(self.connect_button)
        buttons_layout.addWidget(self.disconnect_button)

        # Añadir layout al layout padre
        parent_layout.addLayout(buttons_layout)

    def _setup_connections_list(self, parent_layout) -> None:
        self.list_widget = QListWidget()

        self.list_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        parent_layout.addWidget(self.list_widget)

    # ===============
    # === HELPERS ===
    # ===============

    def _create_icon_button(self, icon_name: str) -> QPushButton:
        button = QPushButton()
        button.setIcon(qta.icon(icon_name))
        button.setFixedSize(32, 32)
        return button

    # ===============
    # === SIGNALS ===
    # ===============

    def _connect_signals(self) -> None:
        """
        Conecta las señales de los widgets con sus callbacks.
        """

        # Lista de conexiones
        self.list_widget.itemSelectionChanged.connect(self._on_selection_changed)

    # ======================
    # === EVENT HANDLERS ===
    # ======================

    def _load_connections(self) -> None:
        """
        Recupera las conexiones desde el servicio y las
        carga en la lista visual.
        """

        self._clear_selection()

        connections = get_connections()

        self.list_widget.clear()

        for connection in connections:
            self._add_connection_item(connection)

    def _add_connection_item(self, connection: Connection) -> None:
        """
        Añade una conexión individual a la lista visual.

        Args:
            connection (Connection):
                Conexión a representar.
        """

        # Texto visible
        connection_name = connection.name or "Sin nombre"

        item = QListWidgetItem(connection_name)

        # Icono según driver
        item.setIcon(self._get_driver_icon(connection.driver))

        # Guardar objeto completo dentro del item
        item.setData(
            Qt.ItemDataRole.UserRole,
            connection,
        )

        self.list_widget.addItem(item)

    def _get_driver_icon(self, driver: Driver) -> QIcon:
        """
        Retorna el icono asociado al driver de base de datos.

        Args:
            driver (Driver):
                Driver asociado a la conexión.

        Returns:
            QIcon:
                Icono correspondiente al driver.
        """

        icons = {
            Driver.POSTGRESQL: QIcon(POSTGRESQL_LOGO),
            Driver.MYSQL: QIcon(MYSQL_LOGO),
            Driver.SQLITE: QIcon(SQLITE_LOGO),
            Driver.ORACLE: QIcon(ORACLE_LOGO),
        }

        return icons.get(driver, QIcon())

    def _on_selection_changed(self) -> None:
        connection = self._get_selected_connection()

        self._update_buttons_state(connection)

        if connection is not None:
            logger.info(f"Conexión seleccionada: {connection}")
            self.connection_selected.emit(connection)
        else:
            logger.info(f"Conexión seleccionada: {None}")

    def _get_selected_connection(self) -> Connection | None:
        """
        Obtiene la conexión seleccionada en la lista.

        Returns:
            Connection:
                El objeto de la conexión.
        """

        item = self.list_widget.currentItem()

        if item is None:
            return None

        return item.data(Qt.ItemDataRole.UserRole)

    def _clear_selection(self) -> None:
        """
        Limpia la selección actual de la lista.
        """

        self.list_widget.clearSelection()
        self.list_widget.setCurrentItem(None)

    # ================
    # === UI STATE ===
    # ================

    def _setup_buttons_state(self) -> None:
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
        Actualiza el estado de los botones según
        la conexión seleccionada.
        """

        has_selection = connection is not None

        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)
        self.connect_button.setEnabled(has_selection)

        # De momento desactivado
        self.disconnect_button.setEnabled(False)

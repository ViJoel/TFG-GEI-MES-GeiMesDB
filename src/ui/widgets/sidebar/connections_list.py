import qtawesome as qta
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from model.connections.connection import Connection
from model.connections.driver import Driver
from service.connections import get_connections
from ui.common.paths import MYSQL_LOGO, ORACLE_LOGO, POSTGRESQL_LOGO, SQLITE_LOGO


class ConnectionsList(QWidget):
    """
    Widget encargado de visualizar y gestionar la lista de conexiones.
    """

    # Señal emitida al seleccionar una conexión
    connection_selected = Signal(Connection)

    def __init__(self):
        super().__init__()

        self._setup_ui()
        self._connect_signals()

        self._load_connections()

    # ===============
    # === Widgets ===
    # ===============

    def _setup_ui(self):
        """
        Configura la interfaz del widget.
        """

        # Layout vertical
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # Botones
        self._buttons()

        # Lista de conexiones
        self._connections_list()

    def _buttons(self):
        # Layout horizontal para botones
        self.buttons_layout = QHBoxLayout()

        # Botones
        self.add_con_btn = self._create_button("fa5s.plus")
        self.edit_con_btn = self._create_button("fa5s.edit")
        self.delete_con_btn = self._create_button("fa5s.trash")
        self.con_btn = self._create_button("mdi.wifi")
        self.discon_btn = self._create_button("mdi.wifi-off")

        # Añadir botones al layout horizontal
        self.buttons_layout.addWidget(self.add_con_btn)
        self.buttons_layout.addWidget(self.edit_con_btn)
        self.buttons_layout.addWidget(self.delete_con_btn)
        self.buttons_layout.addWidget(self.con_btn)
        self.buttons_layout.addWidget(self.discon_btn)

        # Añadir el layout horizontal al vertical
        self.main_layout.addLayout(self.buttons_layout)

    def _create_button(self, icon_name: str) -> QPushButton:
        button = QPushButton()
        button.setIcon(qta.icon(icon_name))
        button.setFixedSize(32, 32)
        return button

    def _connections_list(self):
        self.list_widget = QListWidget()
        self.list_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.main_layout.addWidget(self.list_widget)

    # ===============
    # === Señales ===
    # ===============

    def _connect_signals(self):
        # Lista de conexiones
        self.list_widget.itemClicked.connect(self._on_item_clicked)

        # Botón de añadir conexión
        self.add_con_btn.clicked.connect(self._add_con_btn_clicked)

        # Botón de editar conexión
        self.edit_con_btn.clicked.connect(self._edit_con_btn_clicked)

        # Botón de eliminar conexión
        self.delete_con_btn.clicked.connect(self._delete_con_btn_clicked)

        # Botón de conectar
        self.con_btn.clicked.connect(self._con_btn_clicked)

        # Botón de desconectar
        self.discon_btn.clicked.connect(self._discon_btn_clicked)

    # =================
    # === Servicios ===
    # =================

    def _load_connections(self):
        """
        Recupera las conexiones desde el servicio y las
        carga en la lista visual.
        """

        connections = get_connections()

        self.list_widget.clear()

        for connection in connections:
            self._add_connection_item(connection)

    def _add_connection_item(self, connection: Connection):
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

    def _on_item_clicked(self, item: QListWidgetItem):
        """
        Maneja la selección de elementos de la lista.

        Args:
            item (QListWidgetItem):
                Elemento seleccionado.
        """

        connection = item.data(Qt.ItemDataRole.UserRole)

        print(f"{connection}")

        self.connection_selected.emit(connection)

    def _get_selected_connection(self) -> Connection | None:
        item = self.list_widget.currentItem()

        if item is None:
            return None

        return item.data(Qt.ItemDataRole.UserRole)

    def _add_con_btn_clicked(self):
        print("Botón de añadir conexión clickado")

    def _edit_con_btn_clicked(self):
        print("Botón de editar conexión clickado")

    def _delete_con_btn_clicked(self):
        print("Botón de eliminar conexión clickado")

    def _con_btn_clicked(self):
        print("Botón de conectar clickado")

    def _discon_btn_clicked(self):
        print("Botón de desconectar clickado")

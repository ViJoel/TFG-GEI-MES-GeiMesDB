from PySide6.QtGui import (
    QIcon,
    Qt,
)
from PySide6.QtWidgets import (
    QLabel,
    QWidget,
)

from entities.connection import Connection
from entities.driver import Driver
from modules.sessions.service import has_session
from ui.common.paths import (
    MYSQL_LOGO,
    ORACLE_LOGO,
    POSTGRESQL_LOGO,
    SQLITE_LOGO,
)
from ui.utils.layouts import hbox


class ConnectionItem(QWidget):

    # ============
    # === INIT ===
    # ============

    def __init__(self, connection: Connection) -> None:
        """
        Inicializa el item.

        Args:
            connection (Connection): Objeto de la conexión.
        """

        super().__init__()

        self.connection = connection

        self.setObjectName("connection_item")

        self._setup_ui()

    # ================
    # === UI SETUP ===
    # ================

    def _setup_ui(self) -> None:
        """
        Construye la interfaz principal del widget.
        """

        self.setAttribute(Qt.WidgetAttribute.WA_Hover)

        self.setAttribute(
            Qt.WA_StyledBackground,
            True,
        )

        self.setProperty(
            "state",
            "connected" if has_session(self.connection.id) else "disconnected",
        )

        layout = hbox()
        self.setLayout(layout)

        layout.setSpacing(8)

        icon = QLabel()
        icon.setPixmap(self._get_driver_icon().pixmap(24, 24))
        icon.setFixedSize(24, 24)

        name = QLabel(self.connection.name or "Unnamed")

        layout.addWidget(icon)
        layout.addWidget(name)

    # ================
    # === UI STATE ===
    # ================

    def set_selected(self, selected: bool) -> None:
        """
        Actualiza el estado de selección del item.

        Args:
            selected (bool): Estado de selección.
        """

        self.setProperty("selected", "true" if selected else "false")
        self._refresh_style()

    def _refresh_style(self) -> None:
        """
        Reaplica el estilo del widget.
        """

        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    # ==================
    # === UI HELPERS ===
    # ==================

    def _get_driver_icon(
        self,
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

        return icons.get(self.connection.driver, QIcon())

from PySide6.QtCore import (
    Qt,
    Signal,
)
from PySide6.QtGui import QStandardItem
from PySide6.QtWidgets import QMenu

from entities.driver import Driver
from entities.navigation_tree_action import NavigationTreeAction
from modules.sessions.service import get_session_driver
from ui.widgets.workspace.navigation_tree.tree_node_type import TreeNodeType


class NavigationTreeContextMenu(QMenu):

    # =================
    # === VARIABLES ===
    # =================

    action_requested = Signal(
        NavigationTreeAction,
        str,
    )

    # ============
    # === INIT ===
    # ============

    def __init__(
        self,
        parent,
        item: QStandardItem,
        connection_id: str,
    ) -> None:

        super().__init__(parent)

        self.item = item

        node = item.data(Qt.UserRole)

        self.node_type = node["type"]
        self.data = node["data"]

        self.sgbd_driver = get_session_driver(connection_id)

        self._setup_ui()

    # ================
    # === UI SETUP ===
    # ================

    def _setup_ui(
        self,
    ) -> None:
        """
        Construye el menú contextual según el tipo de nodo.
        """

        match self.node_type:

            case TreeNodeType.TABLES_FOLDER:
                self._build_tables_folder_menu()

            case TreeNodeType.TABLE:
                pass

            case TreeNodeType.COLUMNS_FOLDER:
                pass

            case TreeNodeType.COLUMN:
                pass

            case TreeNodeType.CONSTRAINTS_FOLDER:
                pass

            case TreeNodeType.CONSTRAINT:
                pass

            case TreeNodeType.INDEXES_FOLDER:
                pass

            case TreeNodeType.INDEX:
                pass

            case TreeNodeType.VIEWS_FOLDER:
                pass

            case TreeNodeType.VIEW:
                pass

    # ================
    # === UI STATE ===
    # ================

    # ==================
    # === UI HELPERS ===
    # ==================

    def _build_tables_folder_menu(
        self,
    ) -> None:
        """
        Construye el menú contextual del nodo raíz de tablas.
        """

        generate_select_action = self.addAction(
            "Generate SELECT",
        )

        generate_select_action.triggered.connect(
            self._on_generate_select_tables,
        )

        self.addSeparator()

        show_metadata_action = self.addAction(
            "Show metadata",
        )

        show_metadata_action.triggered.connect(
            self._on_show_tables_metadata,
        )

    # ===============
    # === SIGNALS ===
    # ===============

    # ======================
    # === EVENT HANDLERS ===
    # ======================

    # =====================
    # === EVENT HELPERS ===
    # =====================

    # ====================
    # === QT OVERRIDES ===
    # ====================

    # ===================
    # === PRIVATE API ===
    # ===================

    def _on_generate_select_tables(
        self,
    ) -> None:

        self.action_requested.emit(
            NavigationTreeAction.INSERT_SQL_IN_EDITOR,
            self._generate_tables_metadata(),
        )

    def _on_show_tables_metadata(
        self,
    ) -> None:

        self.action_requested.emit(
            NavigationTreeAction.EXECUTE_SQL,
            self._generate_tables_metadata(),
        )

    def _generate_tables_metadata(
        self,
    ) -> str:

        match self.sgbd_driver:

            case Driver.POSTGRESQL:
                return (
                    "SELECT *\n"
                    "FROM information_schema.tables\n"
                    "WHERE table_schema = 'public'\n"
                    "ORDER BY table_name;"
                )

            case Driver.MYSQL:
                return (
                    "SELECT *\n"
                    "FROM information_schema.tables\n"
                    "WHERE table_schema = DATABASE()\n"
                    "ORDER BY table_name;"
                )

            case Driver.SQLITE:
                return (
                    "SELECT *\n"
                    "FROM sqlite_master\n"
                    "WHERE type = 'table'\n"
                    "ORDER BY name;"
                )

            case Driver.ORACLE:
                return "SELECT *\n" "FROM user_tables\n" "ORDER BY table_name;"

        return ""

    # ==================
    # === PUBLIC API ===
    # ==================

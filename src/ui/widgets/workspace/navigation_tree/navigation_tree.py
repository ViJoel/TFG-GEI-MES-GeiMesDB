from typing import Any

import qtawesome as qta
from PySide6.QtCore import (
    QSortFilterProxyModel,
    Qt,
)
from PySide6.QtGui import (
    QIcon,
    QStandardItem,
    QStandardItemModel,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QLineEdit,
    QTreeView,
    QWidget,
)

from entities.message_type import MessageType
from log.app_logger import get_logger
from modules.sessions.service import get_db_tree
from ui.app.app_actions import notify
from ui.app.app_context import AppContext
from ui.app.worker_error import WorkerError
from ui.utils.layouts import vbox
from ui.widgets.workspace.navigation_tree.tree_node_type import TreeNodeType

logger = get_logger(__name__)


class NavigationTree(QWidget):

    # =================
    # === VARIABLES ===
    # =================

    # ============
    # === INIT ===
    # ============

    def __init__(
        self,
        connection_id: str,
    ) -> None:

        super().__init__()

        self.connection_id = connection_id
        self.data: dict[str, Any] = None

        # Modelo y Proxy para filtrado.
        self._setup_models()

        self._setup_ui()
        self._connect_signals()
        self.refresh()

    # ================
    # === UI SETUP ===
    # ================

    def _setup_ui(
        self,
    ) -> None:
        """
        Construye la interfaz principal del widget.
        """

        layout = vbox(
            ml=4,
            mt=4,
            mr=4,
            mb=4,
            sp=4,
        )
        self.setLayout(layout)

        # Buscador
        self.search_bar = self._create_search_bar()
        layout.addWidget(self.search_bar)

        self.tree_view = self._create_tree_view()
        layout.addWidget(self.tree_view)

    def _setup_models(
        self,
    ) -> None:

        self.model = QStandardItemModel()

        self.proxy_model = QSortFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy_model.setRecursiveFilteringEnabled(True)

    # ================
    # === UI STATE ===
    # ================

    # ==================
    # === UI HELPERS ===
    # ==================

    def _create_search_bar(
        self,
    ) -> QLineEdit:

        search_bar = QLineEdit()
        search_bar.setPlaceholderText("🔍 Filter schema...")
        search_bar.setClearButtonEnabled(True)

        return search_bar

    def _create_tree_view(
        self,
    ) -> QTreeView:

        # Vista de árbol
        tree_view = QTreeView()
        tree_view.setModel(self.proxy_model)
        tree_view.setHeaderHidden(True)
        tree_view.setAnimated(True)
        tree_view.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Menú Contextual
        tree_view.setContextMenuPolicy(Qt.CustomContextMenu)

        return tree_view

    def _create_node(
        self,
        text: str,
        node_type: TreeNodeType,
        data: Any | None = None,
    ) -> QStandardItem:

        item = QStandardItem(text)

        item.setIcon(
            self._get_icon(
                node_type=node_type,
                data=data,
            )
        )

        item.setData(
            {
                "type": node_type,
                "data": data,
            },
            Qt.UserRole,
        )

        return item

    def _create_tables_root_node(
        self,
    ) -> None:

        return self._create_node(
            text="Tables",
            node_type=TreeNodeType.TABLES_FOLDER,
        )

    def _create_table_node(
        self,
        table_name: str,
        table: dict[str, Any],
    ) -> None:

        item = self._create_node(
            text=table_name,
            node_type=TreeNodeType.TABLE,
            data=table,
        )

        if table["columns"]:
            item.appendRow(
                self._create_columns_folder(
                    table["columns"],
                )
            )

        if table["constraints"]:
            item.appendRow(
                self._create_constraints_folder(
                    table["constraints"],
                )
            )

        if table["indexes"]:
            item.appendRow(
                self._create_indexes_folder(
                    table["indexes"],
                )
            )

        return item

    def _create_columns_folder(
        self,
        columns: list[dict[str, Any]],
    ) -> QStandardItem:

        item = self._create_node(
            text="Columns",
            node_type=TreeNodeType.COLUMNS_FOLDER,
        )

        for column in columns:
            item.appendRow(self._create_column_node(column))

        return item

    def _create_column_node(
        self,
        column: dict[str, Any],
    ) -> QStandardItem:

        return self._create_node(
            text=f"{column['name']} : {column['type']}",
            node_type=TreeNodeType.COLUMN,
            data=column,
        )

    def _create_constraints_folder(
        self,
        constraints: list[dict[str, Any]],
    ) -> QStandardItem:

        item = self._create_node(
            text="Constraints",
            node_type=TreeNodeType.CONSTRAINTS_FOLDER,
        )

        for constraint in constraints:
            item.appendRow(self._create_constraint_node(constraint))

        return item

    def _create_constraint_node(
        self,
        constraint: dict[str, Any],
    ) -> QStandardItem:

        text = constraint["name"]

        if constraint["type"] == "PRIMARY_KEY":
            text += f" ({', '.join(constraint['columns'])})"

        elif constraint["type"] == "FOREIGN_KEY":
            text += (
                f" ({', '.join(constraint['columns'])}) → "
                f"{constraint['referred_table']}"
                f"({', '.join(constraint['referred_columns'])})"
            )

        elif constraint["type"] == "UNIQUE":
            text += f" ({', '.join(constraint['columns'])})"

        return self._create_node(
            text=text,
            node_type=TreeNodeType.CONSTRAINT,
            data=constraint,
        )

    def _create_indexes_folder(
        self,
        indexes: list[dict[str, Any]],
    ) -> QStandardItem:

        item = self._create_node(
            text="Indexes",
            node_type=TreeNodeType.INDEXES_FOLDER,
        )

        for index in indexes:
            item.appendRow(self._create_index_node(index))

        return item

    def _create_index_node(
        self,
        index: dict[str, Any],
    ) -> QStandardItem:

        text = f"{index['name']} " f"({', '.join(index['columns'])})"

        return self._create_node(
            text=text,
            node_type=TreeNodeType.INDEX,
            data=index,
        )

    def _create_views_root_node(
        self,
    ) -> QStandardItem:

        return self._create_node(
            text="Views",
            node_type=TreeNodeType.VIEWS_FOLDER,
        )

    def _create_view_node(
        self,
        view_name: str,
        view: dict[str, Any],
    ) -> QStandardItem:

        item = self._create_node(
            text=view_name,
            node_type=TreeNodeType.VIEW,
            data=view,
        )

        if view["columns"]:
            item.appendRow(
                self._create_columns_folder(
                    view["columns"],
                )
            )

        if view["indexes"]:
            item.appendRow(
                self._create_indexes_folder(
                    view["indexes"],
                )
            )

        return item

    def _get_icon(
        self,
        node_type: TreeNodeType,
        data: dict[str, Any] | None = None,
    ) -> QIcon:

        match node_type:

            case TreeNodeType.TABLES_FOLDER:
                icon_name = "mdi.folder-table"
                color = "#f9a825"

            case TreeNodeType.TABLE:
                icon_name = "mdi.table"
                color = "#42a5f5"

            case TreeNodeType.COLUMNS_FOLDER:
                icon_name = "mdi.folder-table-outline"
                color = "#f9a825"

            case TreeNodeType.COLUMN:
                if data["pk"]:
                    icon_name = "mdi.key-variant"
                    color = "#ffca28"
                elif data["fk"]:
                    icon_name = "mdi.link-variant"
                    color = "#03a9f4"
                elif data.get("unique", False):
                    icon_name = "mdi.lock"
                    color = "#fe5d51"
                elif not data.get("nullable", True):
                    icon_name = "mdi.null"
                    color = "#e0e0e0"
                else:
                    icon_name = "mdi6.view-column"
                    color = "#90a4ae"

            case TreeNodeType.CONSTRAINTS_FOLDER:
                icon_name = "mdi.folder-lock"
                color = "#f9a825"

            case TreeNodeType.CONSTRAINT:
                if data["type"] == "PRIMARY_KEY":
                    icon_name = "mdi.key-variant"
                    color = "#ffca28"
                elif data["type"] == "FOREIGN_KEY":
                    icon_name = "mdi.link-variant"
                    color = "#03a9f4"
                elif data["type"] == "UNIQUE":
                    icon_name = "mdi.lock"
                    color = "#fe5d51"
                else:
                    icon_name = "mdi.shield-half-full"
                    color = "#000000"

            case TreeNodeType.INDEXES_FOLDER:
                icon_name = "mdi.folder-cog"
                color = "#f9a825"

            case TreeNodeType.INDEX:
                icon_name = "mdi.lightning-bolt"
                color = "#ab47bc"

            case TreeNodeType.VIEWS_FOLDER:
                icon_name = "mdi6.folder-eye"
                color = "#f9a825"

            case TreeNodeType.VIEW:
                if data["is_materialized"]:
                    icon_name = "mdi.table-headers-eye"
                    color = "#42a5f5"
                else:
                    icon_name = "mdi6.table-eye"
                    color = "#26a69a"

            case _:
                icon_name = "mdi.help-circle-outline"
                color = "#9e9e9e"

        return qta.icon(
            icon_name,
            color=color,
        )

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

        self.search_bar.textChanged.connect(
            self._on_filter_changed,
        )

        """
        self.tree_view.customContextMenuRequested.connect(
            self.show_context_menu,
        )
        """

    # ======================
    # === EVENT HANDLERS ===
    # ======================

    def _on_filter_changed(
        self,
        text,
    ) -> None:

        self.proxy_model.setFilterFixedString(text)

        if text:
            self.tree_view.expandAll()

    # =====================
    # === EVENT HELPERS ===
    # =====================

    # ====================
    # === QT OVERRIDES ===
    # ====================

    # ===================
    # === PRIVATE API ===
    # ===================

    def _load_data(
        self,
    ) -> None:

        AppContext.get_task_manager().run(
            get_db_tree,
            self.connection_id,
            on_success=self._load_data_success,
            on_error=self._load_data_error,
        )

    def _load_data_success(
        self,
        data: dict[str, Any],
    ) -> None:

        self.model.clear()

        # ==========
        # Tables
        # ==========

        if data["tables"]:

            tables_root = self._create_tables_root_node()

            for table_name, table in data["tables"].items():
                tables_root.appendRow(
                    self._create_table_node(
                        table_name=table_name,
                        table=table,
                    )
                )

            self.model.appendRow(tables_root)

            self.tree_view.expand(
                self.proxy_model.mapFromSource(
                    tables_root.index(),
                )
            )

        # =========
        # Views
        # =========

        if data["views"]:

            views_root = self._create_views_root_node()

            for view_name, view in data["views"].items():
                views_root.appendRow(
                    self._create_view_node(
                        view_name=view_name,
                        view=view,
                    )
                )

            self.model.appendRow(views_root)

            self.tree_view.expand(
                self.proxy_model.mapFromSource(
                    views_root.index(),
                )
            )

        self.data = data

        notify(
            message_type=MessageType.SUCCESS,
            message="Tree loaded.",
        )

    def _load_data_error(
        self,
        error: WorkerError,
    ) -> None:

        logger.error(f"Error loading tree.\n{error.traceback}")

        notify(
            MessageType.ERROR,
            "Error loading tree.\nSee logs for details.",
        )

    # ==================
    # === PUBLIC API ===
    # ==================

    def refresh(
        self,
    ) -> None:

        notify(
            message_type=MessageType.WARNING,
            message="Loading tree...",
        )

        self._load_data()


"""
📁
👁️
⚡
🔗
🛡️
📄
🔒
🔑
"""

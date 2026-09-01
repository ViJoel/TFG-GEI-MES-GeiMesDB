from typing import Any

import qtawesome as qta
from PySide6.QtCore import (
    QModelIndex,
    QPoint,
    QSortFilterProxyModel,
    Qt,
    Signal,
)
from PySide6.QtGui import (
    QIcon,
    QStandardItem,
    QStandardItemModel,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QLineEdit,
    QPushButton,
    QTreeView,
    QWidget,
)

from entities.message_type import MessageType
from entities.navigation_tree_action import NavigationTreeAction
from log.app_logger import get_logger
from modules.sessions.service import get_db_tree
from ui.app.app_actions import notify
from ui.app.app_context import AppContext
from ui.app.worker_error import WorkerError
from ui.themes.theme_manager import ThemeManager
from ui.translations.translation_manager import TranslationManager
from ui.utils.layouts import (
    hbox,
    vbox,
)
from ui.widgets.workspace.navigation_tree.navigation_tree_context_menu import (
    NavigationTreeContextMenu,
)
from ui.widgets.workspace.navigation_tree.tree_node_type import TreeNodeType

logger = get_logger(__name__)


class NavigationTree(QWidget):
    """
    Árbol de navegación de la base de datos.

    Muestra la estructura del esquema de la conexión
    activa (tablas, vistas y sus objetos asociados)
    y proporciona acciones contextuales para generar
    consultas SQL e interactuar con los distintos
    elementos de la base de datos.

    Además, coordina la recarga del modelo del árbol
    cuando cambia el esquema de la base de datos y
    notifica al resto de la aplicación para que
    actualice los componentes que dependen de dicha
    información, como el autocompletador SQL.
    """

    # =================
    # === VARIABLES ===
    # =================

    action_requested = Signal(
        NavigationTreeAction,
        str,
    )

    tree_reloaded = Signal(dict)

    # ============
    # === INIT ===
    # ============

    def __init__(
        self,
        connection_id: str,
    ) -> None:
        """
        Inicializa el árbol de navegación.

        Args:
            connection_id (str):
                Id de la conexión.
        """

        super().__init__()

        self.connection_id = connection_id

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

        self.setObjectName("navigation_tree")

        self.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground,
            True,
        )

        layout = vbox(
            ml=4,
            mt=4,
            mr=4,
            mb=4,
            sp=4,
        )
        self.setLayout(layout)

        search_layout = hbox(
            sp=4,
        )

        # Buscador
        self.search_bar = self._create_search_bar()
        search_layout.addWidget(self.search_bar)

        # Botón de refresco
        self.refresh_button = self._create_refresh_button()
        search_layout.addWidget(self.refresh_button)

        layout.addLayout(search_layout)

        # Árbol
        self.tree_view = self._create_tree_view()
        layout.addWidget(self.tree_view)

        self._retranslate_ui()

    def _setup_models(
        self,
    ) -> None:
        """
        Inicializa el modelo de datos del árbol y el modelo
        proxy utilizado para aplicar el filtrado de nodos.
        """

        self.model = QStandardItemModel()

        self.proxy_model = QSortFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy_model.setRecursiveFilteringEnabled(True)

    def _retranslate_ui(
        self,
    ) -> None:
        """
        Actualiza todos los textos traducibles del widget.

        Los textos se generan en el momento de la llamada
        utilizando el traductor activo de Qt, permitiendo
        refrescar la interfaz después de cambiar el idioma
        de la aplicación.
        """

        self.refresh_button.setToolTip(
            self.tr("Refresh tree."),
        )

        self.search_bar.setPlaceholderText(
            self.tr("🔍 Filter schema..."),
        )

        self._retranslate_tree()

    # ==================
    # === UI HELPERS ===
    # ==================

    def _create_search_bar(
        self,
    ) -> QLineEdit:
        """
        Crea y configura la barra de búsqueda del árbol.

        Returns:
            QLineEdit:
                Barra de búsqueda configurada para filtrar
                los elementos del árbol.
        """

        search_bar = QLineEdit()
        search_bar.setObjectName("navigation_tree_search_bar")
        search_bar.setClearButtonEnabled(True)

        return search_bar

    def _create_refresh_button(
        self,
    ) -> QPushButton:
        """
        Crea y configura el botón utilizado para recargar
        el contenido del árbol.

        Returns:
            QPushButton:
                Botón de actualización configurado.
        """

        button = QPushButton()

        button.setObjectName("navigation_tree_refresh_button")

        button.setIcon(
            qta.icon(
                "mdi.refresh",
                color=ThemeManager.get_color(
                    "navigation_tree_refresh_button_color",
                ),
            )
        )

        return button

    def _create_tree_view(
        self,
    ) -> QTreeView:
        """
        Crea y configura la vista utilizada para mostrar
        el árbol de navegación.

        Returns:
            QTreeView:
                Vista de árbol configurada con el modelo proxy
                y el menú contextual.
        """

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
        """
        Crea un nodo del árbol con su texto, icono y
        información asociada.

        Args:
            text (str):
                Texto que se mostrará en el nodo.

            node_type (TreeNodeType):
                Tipo de nodo representado.

            data (Any | None):
                Datos asociados al nodo.

        Returns:
            QStandardItem:
                Nodo configurado para incorporarse al modelo
                del árbol.
        """

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
        """
        Crea el nodo raíz que contiene las tablas de la base
        de datos.

        Returns:
            QStandardItem:
                Nodo raíz de las tablas.
        """

        return self._create_node(
            text=self.tr("Tables"),
            node_type=TreeNodeType.TABLES_FOLDER,
        )

    def _create_table_node(
        self,
        table_name: str,
        table: dict[str, Any],
    ) -> None:
        """
        Crea un nodo de tabla y sus nodos secundarios.

        Los nodos secundarios representan las columnas,
        restricciones e índices asociados a la tabla.

        Args:
            table_name (str):
                Nombre de la tabla.

            table (dict[str, Any]):
                Datos de la tabla.

        Returns:
            QStandardItem:
                Nodo de la tabla con sus elementos asociados.
        """

        item = self._create_node(
            text=table_name,
            node_type=TreeNodeType.TABLE,
            data=table,
        )

        if table["columns"]:
            item.appendRow(
                self._create_columns_folder(
                    table["columns"],
                    table_name=table_name,
                )
            )

        if table["constraints"]:
            item.appendRow(
                self._create_constraints_folder(
                    constraints=table["constraints"],
                    table_name=table_name,
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
        table_name: str,
    ) -> QStandardItem:
        """
        Crea el nodo contenedor de las columnas de una tabla
        o vista.

        Args:
            columns (list[dict[str, Any]]):
                Datos de las columnas.

            table_name (str):
                Nombre de la tabla o vista a la que pertenecen.

        Returns:
            QStandardItem:
                Nodo contenedor de las columnas.
        """

        item = self._create_node(
            text=self.tr("Columns"),
            node_type=TreeNodeType.COLUMNS_FOLDER,
        )

        for column in columns:
            item.appendRow(
                self._create_column_node(
                    column=column,
                    table_name=table_name,
                )
            )

        return item

    def _create_column_node(
        self,
        column: dict[str, Any],
        table_name: str,
    ) -> QStandardItem:
        """
        Crea un nodo correspondiente a una columna.

        Args:
            column (dict[str, Any]):
                Datos de la columna.

            table_name (str):
                Nombre de la tabla o vista a la que pertenece.

        Returns:
            QStandardItem:
                Nodo de la columna.
        """

        column["table"] = table_name

        return self._create_node(
            text=f"{column['name']} : {column['type']}",
            node_type=TreeNodeType.COLUMN,
            data=column,
        )

    def _create_constraints_folder(
        self,
        constraints: list[dict[str, Any]],
        table_name: str,
    ) -> QStandardItem:
        """
        Crea el nodo contenedor de las restricciones de una
        tabla.

        Args:
            constraints (list[dict[str, Any]]):
                Datos de las restricciones.

            table_name (str):
                Nombre de la tabla a la que pertenecen.

        Returns:
            QStandardItem:
                Nodo contenedor de las restricciones.
        """

        item = self._create_node(
            text=self.tr("Constraints"),
            node_type=TreeNodeType.CONSTRAINTS_FOLDER,
        )

        for constraint in constraints:
            item.appendRow(
                self._create_constraint_node(
                    constraint=constraint,
                    table_name=table_name,
                )
            )

        return item

    def _create_constraint_node(
        self,
        constraint: dict[str, Any],
        table_name: str,
    ) -> QStandardItem:
        """
        Crea un nodo correspondiente a una restricción.

        El texto mostrado se adapta al tipo de restricción
        e incluye la información relevante de sus columnas
        o tablas relacionadas.

        Args:
            constraint (dict[str, Any]):
                Datos de la restricción.

            table_name (str):
                Nombre de la tabla a la que pertenece.

        Returns:
            QStandardItem:
                Nodo de la restricción.
        """

        text = constraint["name"] or constraint["type"]

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

        elif constraint["type"] == "CHECK":
            text += f" ({constraint['sqltext']})"

        constraint["table"] = table_name

        return self._create_node(
            text=text,
            node_type=TreeNodeType.CONSTRAINT,
            data=constraint,
        )

    def _create_indexes_folder(
        self,
        indexes: list[dict[str, Any]],
    ) -> QStandardItem:
        """
        Crea el nodo contenedor de los índices de una tabla
        o vista.

        Args:
            indexes (list[dict[str, Any]]):
                Datos de los índices.

        Returns:
            QStandardItem:
                Nodo contenedor de los índices.
        """

        item = self._create_node(
            text=self.tr("Indexes"),
            node_type=TreeNodeType.INDEXES_FOLDER,
        )

        for index in indexes:
            item.appendRow(self._create_index_node(index))

        return item

    def _create_index_node(
        self,
        index: dict[str, Any],
    ) -> QStandardItem:
        """
        Crea un nodo correspondiente a un índice.

        Args:
            index (dict[str, Any]):
                Datos del índice.

        Returns:
            QStandardItem:
                Nodo del índice.
        """

        text = f"{index['name']} " f"({', '.join(index['columns'])})"

        return self._create_node(
            text=text,
            node_type=TreeNodeType.INDEX,
            data=index,
        )

    def _create_views_root_node(
        self,
    ) -> QStandardItem:
        """
        Crea el nodo raíz que contiene las vistas de la base
        de datos.

        Returns:
            QStandardItem:
                Nodo raíz de las vistas.
        """

        return self._create_node(
            text=self.tr("Views"),
            node_type=TreeNodeType.VIEWS_FOLDER,
        )

    def _create_view_node(
        self,
        view_name: str,
        view: dict[str, Any],
    ) -> QStandardItem:
        """
        Crea un nodo de vista y sus nodos secundarios.

        Los nodos secundarios representan las columnas e
        índices asociados a la vista.

        Args:
            view_name (str):
                Nombre de la vista.

            view (dict[str, Any]):
                Datos de la vista.

        Returns:
            QStandardItem:
                Nodo de la vista con sus elementos asociados.
        """

        item = self._create_node(
            text=view_name,
            node_type=TreeNodeType.VIEW,
            data=view,
        )

        if view["columns"]:
            item.appendRow(
                self._create_columns_folder(
                    columns=view["columns"],
                    table_name=view_name,
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
        """
        Obtiene el icono correspondiente a un tipo de nodo.

        El icono y su color se determinan en función del tipo
        de nodo y, cuando es necesario, de los datos asociados.

        Args:
            node_type (TreeNodeType):
                Tipo de nodo cuyo icono se desea obtener.

            data (dict[str, Any] | None):
                Datos asociados al nodo, utilizados para
                determinar variantes específicas del icono.

        Returns:
            QIcon:
                Icono correspondiente al nodo.
        """

        match node_type:

            case TreeNodeType.TABLES_FOLDER:
                icon_name = "mdi.folder-table"
                color = self._get_icon_color("folder")

            case TreeNodeType.TABLE:
                icon_name = "mdi.table"
                color = self._get_icon_color("table")

            case TreeNodeType.COLUMNS_FOLDER:
                icon_name = "mdi.folder-table-outline"
                color = self._get_icon_color("folder")

            case TreeNodeType.COLUMN:
                if data["pk"]:
                    icon_name = "mdi.key-variant"
                    color = self._get_icon_color("constraint_pk")
                elif data["fk"]:
                    icon_name = "mdi.link-variant"
                    color = self._get_icon_color("constraint_fk")
                elif data.get("unique", False):
                    icon_name = "mdi.lock"
                    color = self._get_icon_color("constraint_unique")
                elif not data.get("nullable", True):
                    icon_name = "mdi.null"
                    color = self._get_icon_color("constraint_nullable")
                else:
                    icon_name = "mdi6.view-column"
                    color = self._get_icon_color("column")

            case TreeNodeType.CONSTRAINTS_FOLDER:
                icon_name = "mdi.folder-lock"
                color = self._get_icon_color("folder")

            case TreeNodeType.CONSTRAINT:
                if data["type"] == "PRIMARY_KEY":
                    icon_name = "mdi.key-variant"
                    color = self._get_icon_color("constraint_pk")
                elif data["type"] == "FOREIGN_KEY":
                    icon_name = "mdi.link-variant"
                    color = self._get_icon_color("constraint_fk")
                elif data["type"] == "UNIQUE":
                    icon_name = "mdi.lock"
                    color = self._get_icon_color("constraint_unique")
                elif data["type"] == "CHECK":
                    icon_name = "mdi.check-bold"
                    color = self._get_icon_color("constraint_check")
                else:
                    icon_name = "mdi.shield-half-full"
                    color = self._get_icon_color("constraint")

            case TreeNodeType.INDEXES_FOLDER:
                icon_name = "mdi.folder-cog"
                color = self._get_icon_color("folder")

            case TreeNodeType.INDEX:
                icon_name = "mdi.lightning-bolt"
                color = self._get_icon_color("index")

            case TreeNodeType.VIEWS_FOLDER:
                icon_name = "mdi6.folder-eye"
                color = self._get_icon_color("folder")

            case TreeNodeType.VIEW:
                if data["is_materialized"]:
                    icon_name = "mdi.table-headers-eye"
                    color = self._get_icon_color("materialized_view")
                else:
                    icon_name = "mdi6.table-eye"
                    color = self._get_icon_color("view")

            case _:
                icon_name = "mdi.help-circle-outline"
                color = self._get_icon_color()

        return qta.icon(
            icon_name,
            color=color,
        )

    def _get_icon_color(
        self,
        color_id: str | None = None,
    ) -> str:
        """
        Obtiene el color solicitado para el icono del árbol
        del tema de color actualmente aplicado.

        Args:
            color_id (str):
                Id del color en el tema.

        Returns:
            str:
                Código del color.
        """

        if color_id is None:
            return ThemeManager.get_color("navigation_tree_icon_color")
        else:
            return ThemeManager.get_color(f"navigation_tree_{color_id}_icon_color")

    def _retranslate_tree(
        self,
    ) -> None:
        """
        Actualiza los textos traducibles de todos los
        nodos del árbol.

        Recorre recursivamente el modelo y sustituye
        únicamente las etiquetas de los nodos
        pertenecientes a la interfaz de usuario
        (carpetas de tablas, vistas, columnas,
        restricciones e índices).
        """

        for row in range(self.model.rowCount()):
            item = self.model.item(row)

            if item is not None:
                self._retranslate_item(item)

    def _retranslate_item(
        self,
        item: QStandardItem,
    ) -> None:
        """
        Actualiza recursivamente los textos traducibles
        de un nodo y de todos sus descendientes.

        Args:
            item (QStandardItem):
                Nodo raíz desde el que comienza la
                actualización.
        """

        info = item.data(Qt.UserRole)

        match info["type"]:

            case TreeNodeType.TABLES_FOLDER:
                item.setText(
                    self.tr("Tables"),
                )

            case TreeNodeType.VIEWS_FOLDER:
                item.setText(
                    self.tr("Views"),
                )

            case TreeNodeType.COLUMNS_FOLDER:
                item.setText(
                    self.tr("Columns"),
                )

            case TreeNodeType.CONSTRAINTS_FOLDER:
                item.setText(
                    self.tr("Constraints"),
                )

            case TreeNodeType.INDEXES_FOLDER:
                item.setText(
                    self.tr("Indexes"),
                )

        for row in range(item.rowCount()):
            child = item.child(row)
            if child is not None:
                self._retranslate_item(child)

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

        self.refresh_button.clicked.connect(
            self.refresh,
        )

        self.tree_view.collapsed.connect(
            self._on_item_collapsed,
        )

        self.tree_view.customContextMenuRequested.connect(
            self._show_context_menu,
        )

        ThemeManager.events().theme_changed.connect(
            self._on_theme_changed,
        )

        TranslationManager.events().language_changed.connect(
            self._retranslate_ui,
        )

    # ======================
    # === EVENT HANDLERS ===
    # ======================

    def _on_filter_changed(
        self,
        text,
    ) -> None:
        """
        Actualiza el filtro del árbol cuando cambia el texto
        de búsqueda.

        Si existe un filtro activo, expande todos los nodos
        para facilitar la localización de los resultados.
        """

        self.proxy_model.setFilterFixedString(text)

        if text:
            self.tree_view.expandAll()

    def _on_item_collapsed(
        self,
        index: QModelIndex,
    ) -> None:
        """
        Gestiona el colapso de un nodo del árbol.

        Si el elemento seleccionado pertenece al nodo
        colapsado, se elimina la selección y se colapsan
        también sus descendientes.

        Args:
            index (QModelIndex):
                Índice del nodo que ha sido colapsado.
        """

        current = self.tree_view.currentIndex()

        if current.isValid() and self._is_descendant(current, index):
            self.tree_view.clearSelection()
            self.tree_view.setCurrentIndex(QModelIndex())

        self._collapse_children(index)

    def _show_context_menu(
        self,
        pos: QPoint,
    ) -> None:
        """
        Muestra el menú contextual correspondiente al nodo
        situado en la posición indicada.

        Args:
            pos (QPoint):
                Posición del cursor dentro de la vista del árbol.
        """

        index = self.tree_view.indexAt(pos)

        if not index.isValid():
            return

        source_index = self.proxy_model.mapToSource(index)

        item = self.model.itemFromIndex(source_index)

        menu = NavigationTreeContextMenu(
            parent=self,
            item=item,
            connection_id=self.connection_id,
        )

        menu.action_requested.connect(self.action_requested.emit)

        menu.exec(self.tree_view.viewport().mapToGlobal(pos))

    def _on_theme_changed(
        self,
        _: str,
    ) -> None:
        """
        Actualiza todos los recursos dependientes
        del tema.
        """

        self._update_refresh_button_icon()
        self._update_tree_icons()

    # =====================
    # === EVENT HELPERS ===
    # =====================

    def _is_descendant(
        self,
        child: QModelIndex,
        parent: QModelIndex,
    ) -> bool:
        """
        Comprueba si un índice pertenece al subárbol de otro.

        Args:
            child (QModelIndex):
                Índice cuya relación se desea comprobar.

            parent (QModelIndex):
                Índice que se considera antecesor.

        Returns:
            bool:
                True si el índice hijo es el propio padre o
                uno de sus descendientes.
        """

        while child.isValid():

            if child == parent:
                return True

            child = child.parent()

        return False

    def _collapse_children(
        self,
        parent: QModelIndex,
    ) -> None:
        """
        Colapsa recursivamente todos los descendientes de un
        nodo.

        Args:
            parent (QModelIndex):
                Índice del nodo cuyos descendientes se desean
                colapsar.
        """

        model = self.tree_view.model()

        for row in range(model.rowCount(parent)):
            child = model.index(row, 0, parent)

            self._collapse_children(child)
            self.tree_view.collapse(child)

    def _update_refresh_button_icon(
        self,
    ) -> None:
        """
        Actualiza el icono del botón de actualización utilizando
        los colores definidos por el tema actual.
        """

        self.refresh_button.setIcon(
            qta.icon(
                "mdi.refresh",
                color=ThemeManager.get_color(
                    "navigation_tree_refresh_button_color",
                ),
            )
        )

    def _update_tree_icons(
        self,
    ) -> None:
        """
        Actualiza los iconos de todos los nodos del árbol.
        """

        for row in range(self.model.rowCount()):

            item = self.model.item(row)

            if item is not None:
                self._update_item_icons(item)

    def _update_item_icons(
        self,
        item: QStandardItem,
    ) -> None:
        """
        Actualiza recursivamente el icono de un nodo y de todos
        sus descendientes.

        Args:
            item (QStandardItem):
                Nodo a partir del cual se inicia la actualización.
        """

        info = item.data(Qt.UserRole)

        item.setIcon(
            self._get_icon(
                node_type=info["type"],
                data=info["data"],
            )
        )

        for row in range(item.rowCount()):

            child = item.child(row)

            if child is not None:
                self._update_item_icons(child)

    # ===================
    # === PRIVATE API ===
    # ===================

    def _load_data(
        self,
    ) -> None:
        """
        Inicia la carga asíncrona del esquema de la base de
        datos asociado a la conexión actual.
        """

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
        """
        Procesa los datos del esquema obtenidos correctamente
        y reconstruye el contenido del árbol de navegación.

        Una vez cargado el árbol, notifica mediante una señal
        que los datos han sido actualizados.

        Args:
            data (dict[str, Any]):
                Datos del esquema de la base de datos.
        """

        self.model.clear()

        if data is None:
            return

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

        notify(
            message_type=MessageType.SUCCESS,
            message=self.tr("Tree loaded."),
        )

        self.tree_reloaded.emit(data)

    def _load_data_error(
        self,
        error: WorkerError,
    ) -> None:
        """
        Gestiona un error producido durante la carga del
        esquema de la base de datos.

        Registra la información del error y muestra una
        notificación al usuario.

        Args:
            error (WorkerError):
                Información del error producido durante la carga.
        """

        logger.error(f"Error loading tree.\n{error.traceback}")

        notify(
            MessageType.ERROR,
            self.tr("Error loading tree.") + "\n" + self.tr("See logs for details."),
        )

    # ==================
    # === PUBLIC API ===
    # ==================

    def refresh(
        self,
    ) -> None:
        """
        Recarga el esquema de la base de datos y reconstruye
        el árbol de navegación.
        """

        notify(
            message_type=MessageType.WARNING,
            message=self.tr("Loading tree..."),
        )

        self._load_data()

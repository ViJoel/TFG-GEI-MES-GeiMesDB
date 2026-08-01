from PySide6.QtCore import (
    Qt,
    Signal,
)
from PySide6.QtGui import (
    QGuiApplication,
    QStandardItem,
)
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
        """
        Inicializa el menú contextual del árbol de navegación.

        Obtiene la información del nodo seleccionado, carga el driver de la
        conexión activa y configura las acciones disponibles según el tipo de nodo.

        Args:
            parent:
                Widget padre del menú contextual.

            item (QStandardItem):
                Elemento del árbol sobre el que se ha solicitado
                el menú contextual.

            connection_id (str):
                Identificador de la conexión activa.
        """

        super().__init__(parent)

        self.item = item

        node = item.data(Qt.UserRole)

        self.node_type = node["type"]
        self.data = node["data"]

        self.sgbd_driver = get_session_driver(connection_id)

        # Extraer el nombre de la tabla del nodo padre en el árbol:
        self.parent_item = item.parent()
        self.parent_name = (
            self.parent_item.text() if self.parent_item is not None else None
        )

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

        self.setObjectName("navigation_tree_context_menu")

        match self.node_type:

            case TreeNodeType.TABLES_FOLDER:
                self._build_tables_folder_menu()

            case TreeNodeType.TABLE:
                pass

            case TreeNodeType.COLUMNS_FOLDER:
                self._build_columns_folder_menu()

            case TreeNodeType.COLUMN:
                pass

            case TreeNodeType.CONSTRAINTS_FOLDER:
                self._build_constraints_folder_menu()

            case TreeNodeType.CONSTRAINT:
                pass

            case TreeNodeType.INDEXES_FOLDER:
                self._build_indexes_folder_menu()

            case TreeNodeType.INDEX:
                self._build_index_menu()

            case TreeNodeType.VIEWS_FOLDER:
                self._build_views_folder_menu()

            case TreeNodeType.VIEW:
                pass

    # ==================
    # === UI HELPERS ===
    # ==================

    # Tablas

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

    # Columnas

    def _build_columns_folder_menu(
        self,
    ) -> None:
        """
        Construye el menú contextual del nodo raíz de columnas.
        """

        generate_select_action = self.addAction(
            "Generate SELECT",
        )

        generate_select_action.triggered.connect(
            self._on_generate_select_columns,
        )

        self.addSeparator()

        show_metadata_action = self.addAction(
            "Show metadata",
        )

        show_metadata_action.triggered.connect(
            self._on_show_columns_metadata,
        )

    # Restricciones

    def _build_constraints_folder_menu(
        self,
    ) -> None:
        """
        Construye el menú contextual del nodo raíz de restricciones.
        """

        generate_select_action = self.addAction(
            "Generate SELECT",
        )

        generate_select_action.triggered.connect(
            self._on_generate_select_constraints,
        )

        self.addSeparator()

        show_metadata_action = self.addAction(
            "Show metadata",
        )

        show_metadata_action.triggered.connect(
            self._on_show_constraints_metadata,
        )

    # Índices

    def _build_indexes_folder_menu(
        self,
    ) -> None:
        """
        Construye el menú contextual del nodo raíz de índices.
        """

        generate_select_action = self.addAction(
            "Generate SELECT",
        )

        generate_select_action.triggered.connect(
            self._on_generate_select_indexes,
        )

        self.addSeparator()

        show_metadata_action = self.addAction(
            "Show metadata",
        )

        show_metadata_action.triggered.connect(
            self._on_show_indexes_metadata,
        )

    # Índice

    def _build_index_menu(
        self,
    ) -> None:
        """
        Construye el menú contextual de un índice.
        """

        generate_select_action = self.addAction(
            "Generate SELECT",
        )

        generate_select_action.triggered.connect(
            self._on_generate_select_index,
        )

        self.addSeparator()

        show_details_action = self.addAction(
            "Show details",
        )

        show_details_action.triggered.connect(
            self._on_show_index_details,
        )

        self.addSeparator()

        copy_name_action = self.addAction(
            "Copy name",
        )

        copy_name_action.triggered.connect(
            self._on_copy_index_name,
        )

    # Vistas

    def _build_views_folder_menu(
        self,
    ) -> None:
        """
        Construye el menú contextual del nodo raíz de vistas.
        """

        generate_select_action = self.addAction(
            "Generate SELECT",
        )

        generate_select_action.triggered.connect(
            self._on_generate_select_views,
        )

        self.addSeparator()

        show_metadata_action = self.addAction(
            "Show metadata",
        )

        show_metadata_action.triggered.connect(
            self._on_show_views_metadata,
        )

    # ======================
    # === EVENT HANDLERS ===
    # ======================

    # Tablas

    def _on_generate_select_tables(
        self,
    ) -> None:
        """
        Genera la consulta SQL con la metadata de las tablas
        y solicita su inserción en el editor SQL.
        """

        self.action_requested.emit(
            NavigationTreeAction.INSERT_SQL_IN_EDITOR,
            self._generate_tables_metadata(),
        )

    def _on_show_tables_metadata(
        self,
    ) -> None:
        """
        Genera la consulta SQL con la metadata de las tablas
        y solicita su ejecución.
        """

        self.action_requested.emit(
            NavigationTreeAction.EXECUTE_SQL,
            self._generate_tables_metadata(),
        )

    # Columnas

    def _on_generate_select_columns(
        self,
    ) -> None:
        """
        Genera la consulta SQL con la metadata de las columnas
        y solicita su inserción en el editor SQL.
        """

        self.action_requested.emit(
            NavigationTreeAction.INSERT_SQL_IN_EDITOR,
            self._generate_columns_metadata(),
        )

    def _on_show_columns_metadata(
        self,
    ) -> None:
        """
        Genera la consulta SQL con la metadata de las columnas
        y solicita su ejecución.
        """

        self.action_requested.emit(
            NavigationTreeAction.EXECUTE_SQL,
            self._generate_columns_metadata(),
        )

    # Restricciones

    def _on_generate_select_constraints(
        self,
    ) -> None:
        """
        Genera la consulta SQL con la metadata de las restricciones
        y solicita su inserción en el editor SQL.
        """

        self.action_requested.emit(
            NavigationTreeAction.INSERT_SQL_IN_EDITOR,
            self._generate_constraints_metadata(),
        )

    def _on_show_constraints_metadata(
        self,
    ) -> None:
        """
        Genera la consulta SQL con la metadata de las restricciones
        y solicita su ejecución.
        """

        self.action_requested.emit(
            NavigationTreeAction.EXECUTE_SQL,
            self._generate_constraints_metadata(),
        )

    # Índices

    def _on_generate_select_indexes(
        self,
    ) -> None:
        """
        Genera la consulta SQL con la metadata de los índices
        y solicita su inserción en el editor SQL.
        """

        self.action_requested.emit(
            NavigationTreeAction.INSERT_SQL_IN_EDITOR,
            self._generate_indexes_metadata(),
        )

    def _on_show_indexes_metadata(
        self,
    ) -> None:
        """
        Genera la consulta SQL con la metadata de los índices
        y solicita su ejecución.
        """

        self.action_requested.emit(
            NavigationTreeAction.EXECUTE_SQL,
            self._generate_indexes_metadata(),
        )

    # Índice

    def _on_generate_select_index(
        self,
    ) -> None:
        """
        Genera la consulta SQL con el detalle del índice seleccionado
        y solicita su inserción en el editor SQL.
        """

        self.action_requested.emit(
            NavigationTreeAction.INSERT_SQL_IN_EDITOR,
            self._generate_index_details(),
        )

    def _on_show_index_details(
        self,
    ) -> None:
        """
        Genera la consulta SQL con el detalle del índice seleccionado
        y solicita su ejecución.
        """

        self.action_requested.emit(
            NavigationTreeAction.EXECUTE_SQL,
            self._generate_index_details(),
        )

    def _on_copy_index_name(
        self,
    ) -> None:
        """
        Copia al portapapeles el nombre del índice seleccionado.
        """

        QGuiApplication.clipboard().setText(
            self.data["name"],
        )

    # Vistas

    def _on_generate_select_views(
        self,
    ) -> None:
        """
        Genera la consulta SQL con la metadata de las vistas
        y solicita su inserción en el editor SQL.
        """

        self.action_requested.emit(
            NavigationTreeAction.INSERT_SQL_IN_EDITOR,
            self._generate_views_metadata(),
        )

    def _on_show_views_metadata(
        self,
    ) -> None:
        """
        Genera la consulta SQL con la metadata de las vistas
        y solicita su ejecución.
        """

        self.action_requested.emit(
            NavigationTreeAction.EXECUTE_SQL,
            self._generate_views_metadata(),
        )

    # ===================
    # === PRIVATE API ===
    # ===================

    # Tablas

    def _generate_tables_metadata(
        self,
    ) -> str:
        """
        Genera la consulta SQL para obtener la metadata de las tablas
        según el sistema gestor de base de datos activo.

        Returns:
            str:
                Consulta SQL compatible con el driver configurado.
        """

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

    # Columnas

    def _generate_columns_metadata(
        self,
    ) -> str:
        """
        Genera la consulta SQL para obtener la metadata de las columnas
        de la tabla seleccionada según el sistema gestor de base de datos activo.

        Returns:
            str:
                Consulta SQL compatible con el driver configurado.
        """

        match self.sgbd_driver:

            case Driver.POSTGRESQL:
                return (
                    "SELECT *\n"
                    "FROM information_schema.columns\n"
                    "WHERE table_schema = 'public'\n"
                    f"AND table_name = '{self.parent_name}'\n"
                    "ORDER BY ordinal_position;"
                )

            case Driver.MYSQL:
                return (
                    "SELECT *\n"
                    "FROM information_schema.columns\n"
                    "WHERE table_schema = DATABASE()\n"
                    f"AND table_name = '{self.parent_name}'\n"
                    "ORDER BY ordinal_position;"
                )

            case Driver.SQLITE:
                return f"PRAGMA table_info('{self.parent_name}');"

            case Driver.ORACLE:
                return (
                    "SELECT *\n"
                    "FROM user_tab_columns\n"
                    f"WHERE table_name = '{self.parent_name.upper()}'\n"
                    "ORDER BY column_id;"
                )

        return ""

    # Restricciones

    def _generate_constraints_metadata(
        self,
    ) -> str:
        """
        Genera la consulta SQL para obtener la metadata de las restricciones
        de la tabla seleccionada según el sistema gestor de base de datos activo.

        Returns:
            str:
                Consulta SQL compatible con el driver configurado.
        """

        match self.sgbd_driver:

            case Driver.POSTGRESQL:
                return (
                    "SELECT *\n"
                    "FROM information_schema.table_constraints\n"
                    "WHERE constraint_schema = 'public'\n"
                    f"AND table_name = '{self.parent_name}'\n"
                    "ORDER BY constraint_name;"
                )

            case Driver.MYSQL:
                return (
                    "SELECT *\n"
                    "FROM information_schema.table_constraints\n"
                    "WHERE constraint_schema = DATABASE()\n"
                    f"AND table_name = '{self.parent_name}'\n"
                    "ORDER BY constraint_name;"
                )

            case Driver.SQLITE:
                return (
                    "SELECT *\n"
                    "FROM sqlite_master\n"
                    "WHERE type = 'table'\n"
                    f"AND name = '{self.parent_name}';"
                )

            case Driver.ORACLE:
                return (
                    "SELECT *\n"
                    "FROM user_constraints\n"
                    f"WHERE table_name = '{self.parent_name.upper()}'\n"
                    "ORDER BY constraint_name;"
                )

        return ""

    # Índices

    def _generate_indexes_metadata(
        self,
    ) -> str:
        """
        Genera la consulta SQL para obtener la metadata de los índices
        de la tabla seleccionada según el sistema gestor de base de datos activo.

        Returns:
            str:
                Consulta SQL compatible con el driver configurado.
        """

        match self.sgbd_driver:

            case Driver.POSTGRESQL:
                return (
                    "SELECT *\n"
                    "FROM pg_indexes\n"
                    "WHERE schemaname = 'public'\n"
                    f"AND tablename = '{self.parent_name}'\n"
                    "ORDER BY indexname;"
                )

            case Driver.MYSQL:
                return (
                    "SELECT *\n"
                    "FROM information_schema.statistics\n"
                    "WHERE table_schema = DATABASE()\n"
                    f"AND table_name = '{self.parent_name}'\n"
                    "ORDER BY index_name;"
                )

            case Driver.SQLITE:
                return f"PRAGMA index_list('{self.parent_name}');"

            case Driver.ORACLE:
                return (
                    "SELECT *\n"
                    "FROM user_indexes\n"
                    f"WHERE table_name = '{self.parent_name.upper()}'\n"
                    "ORDER BY index_name;"
                )

        return ""

    # Índice

    def _generate_index_details(
        self,
    ) -> str:
        """
        Genera la consulta SQL para obtener el detalle del índice
        seleccionado según el sistema gestor de base de datos activo.

        Returns:
            str:
                Consulta SQL compatible con el driver configurado.
        """

        match self.sgbd_driver:

            case Driver.POSTGRESQL:
                return (
                    "SELECT *\n"
                    "FROM pg_indexes\n"
                    "WHERE schemaname = 'public'\n"
                    f"AND indexname = '{self.data["name"]}';"
                )

            case Driver.MYSQL:
                return (
                    "SELECT *\n"
                    "FROM information_schema.statistics\n"
                    "WHERE table_schema = DATABASE()\n"
                    f"AND index_name = '{self.data["name"]}';"
                )

            case Driver.SQLITE:
                return (
                    "SELECT *\n"
                    "FROM sqlite_master\n"
                    "WHERE type = 'index'\n"
                    f"AND name = '{self.data["name"]}';"
                )

            case Driver.ORACLE:
                return (
                    "SELECT *\n"
                    "FROM user_indexes\n"
                    f"WHERE index_name = '{self.data['name'].upper()}';"
                )

        return ""

    # Vistas

    def _generate_views_metadata(
        self,
    ) -> str:
        """
        Genera la consulta SQL para obtener la metadata de las vistas
        según el sistema gestor de base de datos activo.

        Returns:
            str:
                Consulta SQL compatible con el driver configurado.
        """

        match self.sgbd_driver:

            case Driver.POSTGRESQL:
                return (
                    "SELECT *\n"
                    "FROM information_schema.views\n"
                    "WHERE table_schema = 'public'\n"
                    "ORDER BY table_name;"
                )

            case Driver.MYSQL:
                return (
                    "SELECT *\n"
                    "FROM information_schema.views\n"
                    "WHERE table_schema = DATABASE()\n"
                    "ORDER BY table_name;"
                )

            case Driver.SQLITE:
                return (
                    "SELECT *\n"
                    "FROM sqlite_master\n"
                    "WHERE type = 'view'\n"
                    "ORDER BY name;"
                )

            case Driver.ORACLE:
                return "SELECT *\n" "FROM user_views\n" "ORDER BY view_name;"

        return ""

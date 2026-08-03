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
                self._build_table_menu()

            case TreeNodeType.COLUMNS_FOLDER:
                self._build_columns_folder_menu()

            case TreeNodeType.COLUMN:
                self._build_column_menu()

            case TreeNodeType.CONSTRAINTS_FOLDER:
                self._build_constraints_folder_menu()

            case TreeNodeType.CONSTRAINT:
                self._build_constraint_menu()

            case TreeNodeType.INDEXES_FOLDER:
                self._build_indexes_folder_menu()

            case TreeNodeType.INDEX:
                self._build_index_menu()

            case TreeNodeType.VIEWS_FOLDER:
                self._build_views_folder_menu()

            case TreeNodeType.VIEW:
                self._build_view_menu()

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

    # Tabla

    def _build_table_menu(
        self,
    ) -> None:
        """
        Construye el menú contextual de una tabla.
        """

        generate_select_action = self.addAction(
            "Generate SELECT",
        )

        generate_select_action.triggered.connect(
            self._on_generate_select_table,
        )

        generate_insert_action = self.addAction(
            "Generate INSERT",
        )

        generate_insert_action.triggered.connect(
            self._on_generate_insert_table,
        )

        generate_update_action = self.addAction(
            "Generate UPDATE",
        )

        generate_update_action.triggered.connect(
            self._on_generate_update_table,
        )

        generate_delete_action = self.addAction(
            "Generate DELETE",
        )

        generate_delete_action.triggered.connect(
            self._on_generate_delete_table,
        )

        generate_alter_action = self.addAction(
            "Generate ALTER",
        )

        generate_alter_action.triggered.connect(
            self._on_generate_alter_table,
        )

        generate_drop_action = self.addAction(
            "Generate DROP",
        )

        generate_drop_action.triggered.connect(
            self._on_generate_drop_table,
        )

        self.addSeparator()

        show_data_action = self.addAction(
            "Show data",
        )

        show_data_action.triggered.connect(
            self._on_show_table_data,
        )

        show_metadata_action = self.addAction(
            "Show metadata",
        )

        show_metadata_action.triggered.connect(
            self._on_show_table_metadata,
        )

        show_columns_action = self.addAction(
            "Show columns",
        )

        show_columns_action.triggered.connect(
            self._on_show_table_columns,
        )

        self.addSeparator()

        copy_name_action = self.addAction(
            "Copy name",
        )

        copy_name_action.triggered.connect(
            self._on_copy_table_name,
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

    # Columna

    def _build_column_menu(
        self,
    ) -> None:
        """
        Construye el menú contextual de una columna.
        """

        generate_select_action = self.addAction(
            "Generate SELECT",
        )

        generate_select_action.triggered.connect(
            self._on_generate_select_column,
        )

        generate_where_action = self.addAction(
            "Generate WHERE",
        )

        generate_where_action.triggered.connect(
            self._on_generate_where_column,
        )

        self.addSeparator()

        show_data_action = self.addAction(
            "Show data",
        )

        show_data_action.triggered.connect(
            self._on_show_column_data,
        )

        show_metadata_action = self.addAction(
            "Show metadata",
        )

        show_metadata_action.triggered.connect(
            self._on_show_column_metadata,
        )

        self.addSeparator()

        copy_name_action = self.addAction(
            "Copy name",
        )

        copy_name_action.triggered.connect(
            self._on_copy_column_name,
        )

        copy_type_action = self.addAction(
            "Copy type",
        )

        copy_type_action.triggered.connect(
            self._on_copy_column_type,
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

    # Restricción

    def _build_constraint_menu(
        self,
    ) -> None:
        """
        Construye el menú contextual de una restricción.
        """

        generate_select_action = self.addAction(
            "Generate SELECT",
        )

        generate_select_action.triggered.connect(
            self._on_generate_select_constraint,
        )

        self.addSeparator()

        show_details_action = self.addAction(
            "Show details",
        )

        show_details_action.triggered.connect(
            self._on_show_constraint_details,
        )

        self.addSeparator()

        copy_name_action = self.addAction(
            "Copy name",
        )

        copy_name_action.triggered.connect(
            self._on_copy_constraint_name,
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

    # Vista

    def _build_view_menu(
        self,
    ) -> None:
        """
        Construye el menú contextual de una vista.
        """

        generate_select_action = self.addAction(
            "Generate SELECT",
        )

        generate_select_action.triggered.connect(
            self._on_generate_select_view,
        )

        generate_drop_action = self.addAction(
            "Generate DROP",
        )

        generate_drop_action.triggered.connect(
            self._on_generate_drop_view,
        )

        self.addSeparator()

        show_data_action = self.addAction(
            "Show data",
        )

        show_data_action.triggered.connect(
            self._on_show_view_data,
        )

        show_metadata_action = self.addAction(
            "Show metadata",
        )

        show_metadata_action.triggered.connect(
            self._on_show_view_metadata,
        )

        show_columns_action = self.addAction(
            "Show columns",
        )

        show_columns_action.triggered.connect(
            self._on_show_view_columns,
        )

        self.addSeparator()

        copy_name_action = self.addAction(
            "Copy name",
        )

        copy_name_action.triggered.connect(
            self._on_copy_view_name,
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

    # Tabla

    def _on_generate_select_table(
        self,
    ) -> None:
        """
        Genera una consulta SELECT para la tabla seleccionada
        y solicita su inserción en el editor SQL.
        """

        self.action_requested.emit(
            NavigationTreeAction.INSERT_SQL_IN_EDITOR,
            self._generate_table_select(),
        )

    def _on_generate_insert_table(
        self,
    ) -> None:
        """
        Genera una consulta INSERT para la tabla seleccionada
        y solicita su inserción en el editor SQL.
        """

        self.action_requested.emit(
            NavigationTreeAction.INSERT_SQL_IN_EDITOR,
            self._generate_table_insert(),
        )

    def _on_generate_update_table(
        self,
    ) -> None:
        """
        Genera una consulta UPDATE para la tabla seleccionada
        y solicita su inserción en el editor SQL.
        """

        self.action_requested.emit(
            NavigationTreeAction.INSERT_SQL_IN_EDITOR,
            self._generate_table_update(),
        )

    def _on_generate_delete_table(
        self,
    ) -> None:
        """
        Genera una consulta DELETE para la tabla seleccionada
        y solicita su inserción en el editor SQL.
        """

        self.action_requested.emit(
            NavigationTreeAction.INSERT_SQL_IN_EDITOR,
            self._generate_table_delete(),
        )

    def _on_generate_alter_table(
        self,
    ) -> None:
        """
        Genera una consulta ALTER para la tabla seleccionada
        y solicita su inserción en el editor SQL.
        """

        self.action_requested.emit(
            NavigationTreeAction.INSERT_SQL_IN_EDITOR,
            self._generate_table_alter(),
        )

    def _on_generate_drop_table(
        self,
    ) -> None:
        """
        Genera una consulta DROP para la tabla seleccionada
        y solicita su inserción en el editor SQL.
        """

        self.action_requested.emit(
            NavigationTreeAction.INSERT_SQL_IN_EDITOR,
            self._generate_table_drop(),
        )

    def _on_show_table_data(
        self,
    ) -> None:
        """
        Genera una consulta SQL para mostrar los datos de la
        tabla seleccionada y solicita su ejecución.
        """

        self.action_requested.emit(
            NavigationTreeAction.EXECUTE_SQL,
            self._generate_table_data(),
        )

    def _on_show_table_metadata(
        self,
    ) -> None:
        """
        Genera una consulta SQL con la metadata de la tabla
        seleccionada y solicita su ejecución.
        """

        self.action_requested.emit(
            NavigationTreeAction.EXECUTE_SQL,
            self._generate_table_metadata(),
        )

    def _on_show_table_columns(
        self,
    ) -> None:
        """
        Genera una consulta SQL con la metadata de las columnas
        de la tabla seleccionada y solicita su ejecución.
        """

        self.action_requested.emit(
            NavigationTreeAction.EXECUTE_SQL,
            self._generate_table_columns(),
        )

    def _on_copy_table_name(
        self,
    ) -> None:
        """
        Copia al portapapeles el nombre de la tabla seleccionada.
        """

        QGuiApplication.clipboard().setText(
            self.item.text(),
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

    # Columna

    def _on_generate_select_column(
        self,
    ) -> None:
        """
        Genera una consulta SQL para seleccionar la columna
        y solicita su inserción en el editor SQL.
        """

        self.action_requested.emit(
            NavigationTreeAction.INSERT_SQL_IN_EDITOR,
            self._generate_column_select(),
        )

    def _on_generate_where_column(
        self,
    ) -> None:
        """
        Genera una cláusula WHERE para la columna seleccionada
        y solicita su inserción en el editor SQL.
        """

        self.action_requested.emit(
            NavigationTreeAction.INSERT_SQL_IN_EDITOR,
            self._generate_column_where(),
        )

    def _on_show_column_data(
        self,
    ) -> None:
        """
        Genera una consulta SQL para mostrar los datos de la
        columna seleccionada y solicita su ejecución.
        """

        self.action_requested.emit(
            NavigationTreeAction.EXECUTE_SQL,
            self._generate_column_data(),
        )

    def _on_show_column_metadata(
        self,
    ) -> None:
        """
        Genera una consulta SQL con la metadata de la columna
        seleccionada y solicita su ejecución.
        """

        self.action_requested.emit(
            NavigationTreeAction.EXECUTE_SQL,
            self._generate_column_metadata(),
        )

    def _on_copy_column_name(
        self,
    ) -> None:
        """
        Copia al portapapeles el nombre de la columna seleccionada.
        """

        QGuiApplication.clipboard().setText(
            self.data["name"],
        )

    def _on_copy_column_type(
        self,
    ) -> None:
        """
        Copia al portapapeles el tipo de la columna seleccionada.
        """

        QGuiApplication.clipboard().setText(
            self.data["type"],
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

    # Restricción

    def _on_generate_select_constraint(
        self,
    ) -> None:
        """
        Genera la consulta SQL con el detalle de la restricción
        seleccionada y solicita su inserción en el editor SQL.
        """

        self.action_requested.emit(
            NavigationTreeAction.INSERT_SQL_IN_EDITOR,
            self._generate_constraint_details(),
        )

    def _on_show_constraint_details(
        self,
    ) -> None:
        """
        Genera la consulta SQL con el detalle de la restricción
        seleccionada y solicita su ejecución.
        """

        self.action_requested.emit(
            NavigationTreeAction.EXECUTE_SQL,
            self._generate_constraint_details(),
        )

    def _on_copy_constraint_name(
        self,
    ) -> None:
        """
        Copia al portapapeles el nombre de la restricción seleccionada.
        """

        QGuiApplication.clipboard().setText(
            self.data["name"],
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

    # Vista

    def _on_generate_select_view(
        self,
    ) -> None:
        """
        Genera una consulta SELECT para la vista seleccionada
        y solicita su inserción en el editor SQL.
        """

        self.action_requested.emit(
            NavigationTreeAction.INSERT_SQL_IN_EDITOR,
            self._generate_view_select(),
        )

    def _on_generate_drop_view(
        self,
    ) -> None:
        """
        Genera una consulta DROP para la vista seleccionada
        y solicita su inserción en el editor SQL.
        """

        self.action_requested.emit(
            NavigationTreeAction.INSERT_SQL_IN_EDITOR,
            self._generate_view_drop(),
        )

    def _on_show_view_data(
        self,
    ) -> None:
        """
        Genera una consulta SQL para mostrar los datos de la
        vista seleccionada y solicita su ejecución.
        """

        self.action_requested.emit(
            NavigationTreeAction.EXECUTE_SQL,
            self._generate_view_data(),
        )

    def _on_show_view_metadata(
        self,
    ) -> None:
        """
        Genera una consulta SQL con la metadata de la vista
        seleccionada y solicita su ejecución.
        """

        self.action_requested.emit(
            NavigationTreeAction.EXECUTE_SQL,
            self._generate_view_metadata(),
        )

    def _on_show_view_columns(
        self,
    ) -> None:
        """
        Genera una consulta SQL con la metadata de las columnas
        de la vista seleccionada y solicita su ejecución.
        """

        self.action_requested.emit(
            NavigationTreeAction.EXECUTE_SQL,
            self._generate_view_columns(),
        )

    def _on_copy_view_name(
        self,
    ) -> None:
        """
        Copia al portapapeles el nombre de la vista seleccionada.
        """

        QGuiApplication.clipboard().setText(
            self.item.text(),
        )

    # =====================
    # === EVENT HELPERS ===
    # =====================

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

    # Tabla

    def _generate_table_select(
        self,
    ) -> str:
        """
        Genera una consulta SELECT para la tabla seleccionada.

        Returns:
            str:
                Consulta SQL.
        """

        return "SELECT *\n" f"FROM {self.item.text()};"

    def _generate_table_insert(
        self,
    ) -> str:
        """
        Genera una consulta INSERT para la tabla seleccionada.

        Returns:
            str:
                Consulta SQL.
        """

        columns = ",\n    ".join(column["name"] for column in self.data["columns"])

        values = ",\n    ".join("?" for _ in self.data["columns"])

        return (
            f"INSERT INTO {self.item.text()} (\n"
            f"    {columns}\n"
            ")\n"
            "VALUES (\n"
            f"    {values}\n"
            ");"
        )

    def _generate_table_update(
        self,
    ) -> str:
        """
        Genera una consulta UPDATE para la tabla seleccionada.

        Returns:
            str:
                Consulta SQL.
        """

        assignments = ",\n    ".join(
            f"{column['name']} = ?" for column in self.data["columns"]
        )

        return f"UPDATE {self.item.text()}\n" "SET\n" f"    {assignments}\n" "WHERE ;"

    def _generate_table_delete(
        self,
    ) -> str:
        """
        Genera una consulta DELETE para la tabla seleccionada.

        Returns:
            str:
                Consulta SQL.
        """

        return f"DELETE FROM {self.item.text()}\n" "WHERE ;"

    def _generate_table_alter(
        self,
    ) -> str:
        """
        Genera una plantilla ALTER para la tabla seleccionada.

        Returns:
            str:
                Consulta SQL.
        """

        return f"ALTER TABLE {self.item.text()}\n" "\n" ";"

    def _generate_table_drop(
        self,
    ) -> str:
        """
        Genera una consulta DROP para la tabla seleccionada.

        Returns:
            str:
                Consulta SQL.
        """

        return f"DROP TABLE {self.item.text()};"

    def _generate_table_data(
        self,
    ) -> str:
        """
        Genera una consulta para mostrar los datos de la tabla
        seleccionada.

        Returns:
            str:
                Consulta SQL.
        """

        return self._generate_table_select()

    def _generate_table_metadata(
        self,
    ) -> str:
        """
        Genera una consulta SQL para obtener la metadata de la
        tabla seleccionada.

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
                    f"AND table_name = '{self.item.text()}';"
                )

            case Driver.MYSQL:
                return (
                    "SELECT *\n"
                    "FROM information_schema.tables\n"
                    "WHERE table_schema = DATABASE()\n"
                    f"AND table_name = '{self.item.text()}';"
                )

            case Driver.SQLITE:
                return (
                    "SELECT *\n"
                    "FROM sqlite_master\n"
                    "WHERE type = 'table'\n"
                    f"AND name = '{self.item.text()}';"
                )

            case Driver.ORACLE:
                return (
                    "SELECT *\n"
                    "FROM user_tables\n"
                    f"WHERE table_name = '{self.item.text().upper()}';"
                )

        return ""

    def _generate_table_columns(
        self,
    ) -> str:
        """
        Genera una consulta SQL para obtener la metadata de las
        columnas de la tabla seleccionada.

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
                    f"AND table_name = '{self.item.text()}'\n"
                    "ORDER BY ordinal_position;"
                )

            case Driver.MYSQL:
                return (
                    "SELECT *\n"
                    "FROM information_schema.columns\n"
                    "WHERE table_schema = DATABASE()\n"
                    f"AND table_name = '{self.item.text()}'\n"
                    "ORDER BY ordinal_position;"
                )

            case Driver.SQLITE:
                return f"PRAGMA table_info('{self.item.text()}');"

            case Driver.ORACLE:
                return (
                    "SELECT *\n"
                    "FROM user_tab_columns\n"
                    f"WHERE table_name = '{self.item.text().upper()}'\n"
                    "ORDER BY column_id;"
                )

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

    # Columna

    def _generate_column_select(
        self,
    ) -> str:
        """
        Genera una consulta SQL para seleccionar la columna.

        Returns:
            str:
                Consulta SQL compatible con el driver configurado.
        """

        return f"SELECT {self.data['name']}\n" f"FROM {self.data['table']};"

    def _generate_column_where(
        self,
    ) -> str:
        """
        Genera una cláusula WHERE para la columna seleccionada.

        Returns:
            str:
                Cláusula WHERE.
        """

        return f"WHERE {self.data['name']} = "

    def _generate_column_data(
        self,
    ) -> str:
        """
        Genera una consulta SQL para mostrar los datos de la
        columna seleccionada.

        Returns:
            str:
                Consulta SQL.
        """

        return f"SELECT {self.data['name']}\n" f"FROM {self.data['table']};"

    def _generate_column_metadata(
        self,
    ) -> str:
        """
        Genera la consulta SQL para obtener la metadata de la
        columna seleccionada según el sistema gestor de base de
        datos activo.

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
                    f"AND table_name = '{self.data['table']}'\n"
                    f"AND column_name = '{self.data['name']}';"
                )

            case Driver.MYSQL:
                return (
                    "SELECT *\n"
                    "FROM information_schema.columns\n"
                    "WHERE table_schema = DATABASE()\n"
                    f"AND table_name = '{self.data['table']}'\n"
                    f"AND column_name = '{self.data['name']}';"
                )

            case Driver.SQLITE:
                return f"PRAGMA table_info('{self.data['table']}');"

            case Driver.ORACLE:
                return (
                    "SELECT *\n"
                    "FROM user_tab_columns\n"
                    f"WHERE table_name = '{self.data['table'].upper()}'\n"
                    f"AND column_name = '{self.data['name'].upper()}';"
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

    # Restricción

    def _generate_constraint_details(
        self,
    ) -> str:
        """
        Genera la consulta SQL para obtener el detalle de la restricción
        seleccionada según el sistema gestor de base de datos activo.

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
                    f"AND constraint_name = '{self.data['name']}';"
                )

            case Driver.MYSQL:
                return (
                    "SELECT *\n"
                    "FROM information_schema.table_constraints\n"
                    "WHERE constraint_schema = DATABASE()\n"
                    f"AND constraint_name = '{self.data['name']}';"
                )

            case Driver.SQLITE:
                return (
                    "SELECT *\n"
                    "FROM sqlite_master\n"
                    "WHERE type = 'table'\n"
                    f"AND name = '{self.data['table']}';"
                )

            case Driver.ORACLE:
                return (
                    "SELECT *\n"
                    "FROM user_constraints\n"
                    f"WHERE constraint_name = '{self.data['name'].upper()}';"
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

    # Vista

    def _generate_view_select(
        self,
    ) -> str:
        """
        Genera una consulta SELECT para la vista seleccionada.

        Returns:
            str:
                Consulta SQL.
        """

        return self._generate_table_select()

    def _generate_view_drop(
        self,
    ) -> str:
        """
        Genera una consulta DROP para la vista seleccionada.

        Returns:
            str:
                Consulta SQL.
        """

        return f"DROP VIEW {self.item.text()};"

    def _generate_view_data(
        self,
    ) -> str:
        """
        Genera una consulta para mostrar los datos de la vista
        seleccionada.

        Returns:
            str:
                Consulta SQL.
        """

        return self._generate_table_data()

    def _generate_view_metadata(
        self,
    ) -> str:
        """
        Genera una consulta SQL para obtener la metadata de la
        vista seleccionada.

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
                    f"AND table_name = '{self.item.text()}';"
                )

            case Driver.MYSQL:
                return (
                    "SELECT *\n"
                    "FROM information_schema.views\n"
                    "WHERE table_schema = DATABASE()\n"
                    f"AND table_name = '{self.item.text()}';"
                )

            case Driver.SQLITE:
                return (
                    "SELECT *\n"
                    "FROM sqlite_master\n"
                    "WHERE type = 'view'\n"
                    f"AND name = '{self.item.text()}';"
                )

            case Driver.ORACLE:
                return (
                    "SELECT *\n"
                    "FROM user_views\n"
                    f"WHERE view_name = '{self.item.text().upper()}';"
                )

        return ""

    def _generate_view_columns(
        self,
    ) -> str:
        """
        Genera una consulta SQL para obtener la metadata de las
        columnas de la vista seleccionada.

        Returns:
            str:
                Consulta SQL compatible con el driver configurado.
        """

        return self._generate_table_columns()

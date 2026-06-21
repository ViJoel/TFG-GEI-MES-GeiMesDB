import logging

from PySide6.QtWidgets import QWidget

from entities.connection import Connection
from modules.sessions.service import execute_query, execute_script, is_editable_query
from ui.state.state import get_selected_connection
from ui.utils.layouts import hbox, vbox
from ui.widgets.workspace.results_view.results_view import ResultsView
from ui.widgets.workspace.sql_editor.sql_editor import SqlEditor
from ui.widgets.workspace.sql_editor.sql_scope import SqlScope

logger = logging.getLogger(__name__)


class Workspace(QWidget):
    """
    Widget principal encargado de coordinar
    la edición y ejecución de consultas SQL.

    Responsabilidades:
    - Gestionar las solicitudes de ejecución
      provenientes del editor SQL.
    - Mostrar los resultados obtenidos.
    - Gestionar la persistencia de cambios
      realizados sobre los datos.
    """

    # ============
    # === INIT ===
    # ============

    def __init__(
        self,
    ) -> None:
        """
        Inicializa el espacio de trabajo.
        """

        super().__init__()

        self._setup_ui()
        self._connect_signals()

    # ================
    # === UI SETUP ===
    # ================

    def _setup_ui(
        self,
    ) -> None:
        """
        Construye la interfaz principal del widget.
        """
        main_layout = hbox()
        self.setLayout(main_layout)

        sql_layout = vbox()
        main_layout.addLayout(sql_layout)

        self.sql_editor = SqlEditor()
        sql_layout.addWidget(self.sql_editor)

        self.results_view = ResultsView()
        sql_layout.addWidget(self.results_view)

    # ===============
    # === SIGNALS ===
    # ===============

    def _connect_signals(
        self,
    ) -> None:
        """
        Conecta las señales de los widgets
        con sus handlers correspondientes.
        """

        self.sql_editor.execute_requested.connect(
            self._on_execute_requested,
        )

        self.results_view.save_requested.connect(
            self._on_save_requested,
        )

    # ======================
    # === EVENT HANDLERS ===
    # ======================

    def _on_execute_requested(
        self,
        sql: list[str],
        scope: SqlScope,
    ) -> None:
        """
        Gestiona las solicitudes de ejecución
        emitidas por el editor SQL.

        Args:
            sql (list[str]):
                Lista de sentencias SQL que deben
                ejecutarse.

            scope (SqlScope):
                Ámbito de ejecución solicitado.
        """

        connection = self._get_selected_connection()

        if connection is None:
            return

        if scope == SqlScope.SELECTED_TEXT:

            logger.info(
                f"Query execution requested for "
                f"'{connection.name}' (ID: {connection.id})."
            )

            query = sql[0]
            self.current_query = query

            logger.debug("Executing query...")

            result = execute_query(
                connection_id=connection.id,
                query=query,
            )

            logger.debug("Query execution completed.")

            logger.debug("Updating results view...")

            self.results_view.show_result(
                result=result,
                script_result=None,
                is_script=False,
            )

            self.results_view.set_editable(is_editable_query(query))

            logger.debug("Results view updated.")

            logger.success(
                f"Query executed successfully for "
                f"'{connection.name}' (ID: {connection.id})."
            )

        elif scope == SqlScope.FULL_SCRIPT:

            logger.info(
                f"Script execution requested for "
                f"'{connection.name}' (ID: {connection.id})."
            )

            logger.debug(f"Executing {len(sql)} SQL statements...")

            script_result = execute_script(
                connection_id=connection.id,
                queries=sql,
            )

            logger.debug("Script execution completed.")

            logger.debug("Updating results view...")

            self.results_view.show_result(
                result=None,
                script_result=script_result,
                is_script=True,
            )

            self.results_view.set_editable(False)

            logger.debug("Results view updated.")

            logger.success(
                f"Script executed successfully for "
                f"'{connection.name}' (ID: {connection.id})."
            )

        self.results_view.set_action_buttons_state(False)

    def _on_save_requested(
        self,
    ) -> None:
        """
        Persiste los cambios realizados sobre
        los datos mostrados en la tabla y
        actualiza los resultados.
        """

        connection = self._get_selected_connection()

        if connection is None:
            return

        logger.info(f"Save requested for '{connection.name}' (ID: {connection.id}).")

        logger.debug("Generating UPDATE queries...")

        queries = self.results_view.table.model.generate_update_queries()

        logger.debug(f"{len(queries)} UPDATE queries generated.")

        logger.debug(f"Executing {len(queries)} UPDATE queries...")

        script_result = execute_script(
            connection_id=connection.id,
            queries=queries,
        )

        logger.debug("UPDATE queries execution completed.")

        logger.debug("Executing original query...")

        result = execute_query(
            connection_id=connection.id,
            query=self.current_query,
        )

        logger.debug("Original query execution completed.")

        logger.debug("Refreshing results view...")

        self.results_view.show_result(
            result=result,
            script_result=None,
            is_script=False,
        )

        self.results_view.show_result(
            result=None,
            script_result=script_result,
            is_script=True,
        )

        self.results_view.set_tab_buttons_state(True)
        self.results_view.set_action_buttons_state(True)

        logger.debug("Results view refreshed.")

        logger.success(f"Changes saved for '{connection.name}' (ID: {connection.id}).")

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

        connection = get_selected_connection()

        if connection is None:
            logger.warning("Operation requested without selected connection.")
            return None

        return connection

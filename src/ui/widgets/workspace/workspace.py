import logging

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSplitter, QWidget

from entities.connection import Connection
from entities.message_type import MessageType
from entities.sql_scope import SqlScope
from modules.sessions.service import execute_query, execute_script, is_editable_query
from ui.app.app_actions import notify
from ui.utils.layouts import hbox
from ui.widgets.workspace.results_view.results_view import ResultsView
from ui.widgets.workspace.sql_editor.sql_editor import SqlEditor

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
        connection: Connection,
    ) -> None:
        """
        Inicializa el espacio de trabajo asociado
        a una conexión concreta.

        Args:
            connection (Connection):
                Conexión utilizada para ejecutar
                consultas y operaciones SQL dentro
                del espacio de trabajo.
        """

        super().__init__()

        self.connection = connection
        self.current_query: str | None = None

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

        self.sql_editor = SqlEditor()
        self.results_view = ResultsView()

        self.splitter = QSplitter(Qt.Vertical)

        # Grosor de la barra.
        self.splitter.setHandleWidth(4)

        # Proporciones de tamaño iniciales de los widgets.
        self.splitter.setSizes([1, 3])

        # Evita que alguno de los paneles desaparezca.
        self.splitter.setChildrenCollapsible(False)

        self.splitter.addWidget(self.sql_editor)
        self.splitter.addWidget(self.results_view)

        main_layout.addWidget(self.splitter)

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

        if scope == SqlScope.SELECTED_TEXT:
            self._execute_query(sql)

        elif scope == SqlScope.FULL_SCRIPT:
            self._execute_script(sql)

        self.results_view.set_action_buttons_state(False)

    def _on_save_requested(
        self,
    ) -> None:
        """
        Persiste los cambios realizados sobre
        los datos mostrados en la tabla y
        actualiza los resultados.
        """

        connection = self.connection

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
        self.results_view.set_action_buttons_state(False)

        logger.debug("Results view refreshed.")

        logger.success(f"Changes saved for '{connection.name}' (ID: {connection.id}).")

    # =====================
    # === EVENT HELPERS ===
    # =====================

    def _execute_query(
        self,
        queries: list[str],
    ) -> None:
        """
        Ejecuta una única consulta SQL y muestra
        el resultado obtenido.

        Si se reciben varias sentencias, la
        ejecución se cancela y se notifica al
        usuario para que ejecute el contenido
        como un script.

        Args:
            queries (list[str]):
                Lista de sentencias SQL a ejecutar.
        """

        logger.info(
            f"Query execution requested for "
            f"'{self.connection.name}' (ID: {self.connection.id})."
        )

        if len(queries) > 1:
            string = (
                "Execution aborted.\n"
                + "More than one SQL statement detected in the selected text.\n"
                + "Multiple statements cannot be executed as a single query.\n"
                + "Execute it as a script instead."
            )

            logger.warning(string)

            self.results_view.write_message(
                string,
                MessageType.WARNING,
            )

            self.results_view.show_console()

            notify(
                MessageType.WARNING,
                "Execution aborted.",
            )

            return

        query = queries[0]
        self.current_query = query

        logger.debug("Executing query...")

        result = execute_query(
            connection_id=self.connection.id,
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
            f"'{self.connection.name}' (ID: {self.connection.id})."
        )

    def _execute_script(
        self,
        queries: list[str],
    ) -> None:
        """
        Ejecuta un script compuesto por una o
        varias sentencias SQL y muestra el
        resultado de la ejecución.

        Args:
            queries (list[str]):
                Lista de sentencias SQL que forman
                el script.
        """

        logger.info(
            f"Script execution requested for "
            f"'{self.connection.name}' (ID: {self.connection.id})."
        )

        logger.debug(f"Executing {len(queries)} SQL statements...")

        script_result = execute_script(
            connection_id=self.connection.id,
            queries=queries,
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
            f"'{self.connection.name}' (ID: {self.connection.id})."
        )

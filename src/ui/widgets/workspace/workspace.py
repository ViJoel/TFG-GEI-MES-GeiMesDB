from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QSizePolicy,
    QSplitter,
    QWidget,
)

from entities.connection import Connection
from entities.message_type import MessageType
from entities.navigation_tree_action import NavigationTreeAction
from entities.queries_history_entry import QueriesHistoryEntry
from entities.query_execution import QueryExecution
from entities.script_result import ScriptResult
from entities.sql_scope import SqlScope
from entities.unsaved_changes_count import UnsavedChangesCount
from log.app_logger import get_logger
from modules.queries_history.service import save_queries_history_batch
from modules.sessions.service import (
    execute_query,
    execute_script,
    execute_updates,
    is_editable_query,
)
from ui.app.app_actions import notify
from ui.app.app_context import AppContext
from ui.app.worker_error import WorkerError
from ui.utils.layouts import hbox
from ui.widgets.workspace.navigation_tree.navigation_tree import NavigationTree
from ui.widgets.workspace.results_view.results_view import ResultsView
from ui.widgets.workspace.sql_editor.sql_editor_area import SqlEditorArea

logger = get_logger(__name__)


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

        self.sql_editor_area = SqlEditorArea()
        self.results_view = ResultsView(connection=self.connection)
        self.navigation_tree = NavigationTree(connection_id=self.connection.id)

        splitter = QSplitter(Qt.Vertical)
        splitter.setHandleWidth(4)
        splitter.setSizes([1, 3])
        splitter.setChildrenCollapsible(True)
        splitter.addWidget(self.sql_editor_area)
        splitter.addWidget(self.results_view)

        splitter_2 = QSplitter(Qt.Horizontal)
        splitter_2.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding,
        )
        splitter_2.setHandleWidth(1)
        splitter_2.setSizes([3, 1])
        splitter_2.setChildrenCollapsible(True)

        splitter_2.addWidget(splitter)
        splitter_2.addWidget(self.navigation_tree)

        main_layout.addWidget(splitter_2)

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

        self.sql_editor_area.execute_requested.connect(
            self._on_execute_requested,
        )

        self.results_view.save_requested.connect(
            self._on_save_requested,
        )

        self.results_view.query_selected_from_session_queries_history.connect(
            self._on_query_selected_from_session_queries_history
        )

        self.navigation_tree.action_requested.connect(
            self._on_navigation_tree_action,
        )

        self.navigation_tree.tree_reloaded.connect(
            self.sql_editor_area.force_update_editors_completers
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

        notify(
            MessageType.WARNING,
            "Executing sql...",
        )

        if scope == SqlScope.SELECTED_TEXT:
            if len(sql) > 1:
                self._execute_script(sql)
            else:
                self._execute_query(sql)

        elif scope == SqlScope.ACTUAL_QUERY:
            self._execute_query(sql)

        elif scope == SqlScope.FULL_SCRIPT:
            self._execute_script(sql)

        self._save_queries_history(sql)

        self.results_view.set_action_buttons_state(False)

    def _on_save_requested(
        self,
    ) -> None:
        """
        Persiste los cambios realizados sobre
        los datos mostrados en la tabla y
        actualiza los resultados.
        """

        notify(
            MessageType.WARNING,
            "Saving changes...",
        )

        # Fuerza el repintado de la interfaz para que la
        # notificación sea visible antes de iniciar una
        # operación síncrona potencialmente bloqueante.
        AppContext.get_app().processEvents()

        saving_operation_success: bool = False

        connection = self.connection

        logger.info(f"Save requested for '{connection.name}' (ID: {connection.id}).")

        logger.debug("Generating UPDATE operations...")

        operations = self.results_view.table.model.generate_update_operations()

        logger.debug(f"{len(operations)} UPDATE operations generated.")

        logger.debug(f"Executing {len(operations)} UPDATE operations...")

        script_result = execute_updates(
            connection_id=connection.id,
            operations=operations,
        )

        logger.debug("UPDATE operations execution completed.")

        if not script_result.rolled_back:

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

            self.results_view.set_action_buttons_state(False)

            logger.debug("Results view refreshed.")

            saving_operation_success = True

        else:

            logger.debug(
                "Transaction rolled back. Keeping current table "
                "state so the user can correct the errors."
            )

            saving_operation_success = False

        self.results_view.show_result(
            result=None,
            script_result=script_result,
            is_script=True,
        )

        self.results_view.set_tab_buttons_state(True)

        logger.success(
            f"Save operation finished for "
            f"'{connection.name}' (ID: {connection.id})."
        )

        if saving_operation_success:
            notify(
                MessageType.SUCCESS,
                "Changes saved",
            )

        else:
            notify(
                MessageType.ERROR,
                "Saving changes failed.",
            )

    def _on_query_selected_from_session_queries_history(
        self,
        query: str,
    ) -> None:

        self.sql_editor_area.set_query_text(query)

    def _on_navigation_tree_action(
        self,
        action: NavigationTreeAction,
        sql: str,
    ) -> None:
        """
        Gestiona las acciones emitidas por el árbol de navegación.

        Dependiendo del tipo de acción solicitada, inserta el SQL en el
        editor o lo ejecuta directamente utilizando el mismo flujo de
        ejecución que el resto de la aplicación.

        Args:
            action (NavigationTreeAction):
                Acción solicitada por el menú contextual del árbol.

            sql (str):
                Sentencia SQL asociada a la acción.
        """

        match action:

            case NavigationTreeAction.INSERT_SQL_IN_EDITOR:
                self.sql_editor_area.set_query_text(sql)

            case NavigationTreeAction.EXECUTE_SQL:
                self._execute_query([sql])

    # =====================
    # === EVENT HELPERS ===
    # =====================

    def _execute_query(
        self,
        queries: list[str],
    ) -> None:
        """
        Ejecuta una única consulta SQL en segundo plano.

        Si se reciben varias sentencias, la ejecución
        se cancela y se notifica al usuario para que
        ejecute el contenido como un script.

        La consulta válida se delega al gestor de
        tareas para evitar bloquear el hilo principal
        de la interfaz.

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

        AppContext.get_task_manager().run(
            self._execute_query_backend,
            queries[0],
            on_success=self._on_query_finished,
            on_error=self._on_execution_error,
        )

    def _execute_query_backend(
        self,
        query: str,
    ) -> QueryExecution:
        """
        Ejecuta una consulta SQL en segundo plano.

        Este método contiene únicamente la lógica de
        acceso a datos y está diseñado para ser
        ejecutado mediante el ``TaskManager``.

        Args:
            query (str):
                Consulta SQL a ejecutar.

        Returns:
            QueryExecution:
                Consulta ejecutada junto con el
                resultado obtenido.
        """

        logger.debug("Executing query...")

        result = execute_query(
            connection_id=self.connection.id,
            query=query,
        )

        logger.debug("Query execution completed.")

        return QueryExecution(
            query=query,
            result=result,
        )

    def _on_query_finished(
        self,
        execution: QueryExecution,
    ) -> None:
        """
        Actualiza la interfaz tras finalizar la
        ejecución de una consulta.

        Muestra el resultado obtenido y actualiza el
        estado de edición del visor de resultados.

        Args:
            execution (QueryExecution):
                Información asociada a la consulta
                ejecutada y su resultado.
        """

        self.current_query = execution.query

        logger.debug("Updating results view...")

        self.results_view.show_result(
            result=execution.result,
            script_result=None,
            is_script=False,
        )

        self.results_view.set_editable(is_editable_query(execution.query))

        logger.debug("Results view updated.")

        logger.success(
            f"Query execution finished for "
            f"'{self.connection.name}' (ID: {self.connection.id})."
        )

        notify(
            MessageType.SUCCESS,
            "SQL query executed.",
        )

    def _on_execution_error(
        self,
        error: WorkerError,
    ) -> None:
        """
        Gestiona los errores inesperados producidos
        durante la ejecución de una consulta o script.

        Registra el error en el log y notifica al
        usuario que la operación no pudo completarse.

        Args:
            error (WorkerError):
                Información del error producido por
                el worker.
        """

        logger.error(f"Error during SQL execution.\n{error.traceback}")

        notify(
            message_type=MessageType.ERROR,
            message="Error in execution.",
        )

    def _execute_script(
        self,
        queries: list[str],
    ) -> None:
        """
        Ejecuta un script SQL en segundo plano.

        El script se delega al gestor de tareas
        para evitar bloquear el hilo principal de
        la interfaz.

        Args:
            queries (list[str]):
                Lista de sentencias SQL que forman
                el script.
        """

        logger.info(
            f"Script execution requested for "
            f"'{self.connection.name}' (ID: {self.connection.id})."
        )

        AppContext.get_task_manager().run(
            self._execute_script_backend,
            queries,
            on_success=self._on_script_finished,
            on_error=self._on_execution_error,
        )

    def _execute_script_backend(
        self,
        queries: list[str],
    ) -> ScriptResult:
        """
        Ejecuta un script SQL en segundo plano.

        Este método contiene únicamente la lógica
        de acceso a datos y está diseñado para ser
        ejecutado mediante el ``TaskManager``.

        Args:
            queries (list[str]):
                Sentencias SQL que forman el script.

        Returns:
            ScriptResult:
                Resultado de la ejecución del script.
        """

        logger.debug(f"Executing {len(queries)} SQL statements...")

        script_result = execute_script(
            connection_id=self.connection.id,
            queries=queries,
        )

        logger.debug("Script execution completed.")

        return script_result

    def _on_script_finished(
        self,
        script_result: ScriptResult,
    ) -> None:
        """
        Actualiza la interfaz tras finalizar la
        ejecución de un script.

        Muestra el resultado obtenido y deshabilita
        la edición del visor de resultados.

        Args:
            script_result (ScriptResult):
                Resultado devuelto por la ejecución
                del script.
        """

        logger.debug("Updating results view...")

        self.results_view.show_result(
            result=None,
            script_result=script_result,
            is_script=True,
        )

        self.results_view.set_editable(False)

        logger.debug("Results view updated.")

        logger.success(
            f"Script execution finished for "
            f"'{self.connection.name}' (ID: {self.connection.id})."
        )

        notify(
            MessageType.SUCCESS,
            "SQL script executed.",
        )

    def _save_queries_history(
        self,
        queries: list[str],
    ) -> None:
        """
        Guarda el historial de consultas ejecutadas.

        Actualiza el historial de la sesión de forma
        inmediata y persiste las consultas en segundo
        plano para evitar bloquear la interfaz.

        Args:
            queries (list[str]):
                Consultas SQL ejecutadas.
        """

        notify(
            MessageType.WARNING,
            "Saving queries history...",
        )

        entries: list[QueriesHistoryEntry] = []

        for query in queries:

            entry = QueriesHistoryEntry(
                connection_id=self.connection.id,
                query=query,
            )

            entries.append(entry)

            self.results_view.add_entry_to_session_queries_history(entry=entry)

        AppContext.get_task_manager().run(
            self._save_queries_history_backend,
            entries,
            on_success=self._on_save_queries_history_success,
            on_error=self._on_save_queries_history_error,
        )

    def _save_queries_history_backend(
        self,
        entries: list[QueriesHistoryEntry],
    ) -> None:
        """
        Persiste el historial de consultas en
        segundo plano.
        """

        save_queries_history_batch(
            connection=self.connection,
            entries=entries,
        )

    def _on_save_queries_history_success(
        self,
        _: None,
    ) -> None:
        """
        Notifica que el historial se ha
        almacenado correctamente.
        """

        notify(
            MessageType.SUCCESS,
            "Queries history updated.",
        )

    def _on_save_queries_history_error(
        self,
        error: WorkerError,
    ) -> None:
        """
        Gestiona los errores producidos al
        guardar el historial de consultas.
        """

        logger.error(f"Error updating queries history.\n{error.traceback}")

        notify(
            MessageType.ERROR,
            "Error updating queries history.\nSee logs for details.",
        )

    # ==================
    # === PUBLIC API ===
    # ==================

    def get_unsaved_changes_count(
        self,
    ) -> UnsavedChangesCount:
        """
        Devuelve el número de archivos abiertos que tienen
        cambios sin guardar/procesar.

        Returns:
            UnsavedChangesCount:
                Cambios sin guardar.
        """

        count = self.sql_editor_area.get_unsaved_changes_count()

        if count <= 0:
            return

        return UnsavedChangesCount(
            connection_name=self.connection.name,
            unsaved_changes=count,
        )

from PySide6.QtWidgets import QWidget

from modules.sessions.service import execute_query, execute_script, is_editable_query
from ui.state.state import get_selected_connection
from ui.utils.layouts import hbox, vbox
from ui.widgets.workspace.results_view.results_view import ResultsView
from ui.widgets.workspace.sql_editor.sql_editor import SqlEditor
from ui.widgets.workspace.sql_editor.sql_scope import SqlScope


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

        if scope == SqlScope.SELECTED_TEXT:

            query = sql[0]
            self.current_query = query

            result = execute_query(
                connection_id=get_selected_connection().id,
                query=query,
            )

            self.results_view.show_result(
                result=result,
                script_result=None,
                is_script=False,
            )

            self.results_view.set_editable(is_editable_query(query))

        elif scope == SqlScope.FULL_SCRIPT:

            script_result = execute_script(
                connection_id=get_selected_connection().id,
                queries=sql,
            )

            self.results_view.show_result(
                result=None,
                script_result=script_result,
                is_script=True,
            )

            self.results_view.set_editable(False)

        self.results_view.set_action_buttons_state(False)

    def _on_save_requested(
        self,
    ) -> None:
        """
        Persiste los cambios realizados sobre
        los datos mostrados en la tabla y
        actualiza los resultados.
        """

        queries = self.results_view.table.model.generate_update_queries()

        script_result = execute_script(
            connection_id=get_selected_connection().id,
            queries=queries,
        )

        result = execute_query(
            connection_id=get_selected_connection().id,
            query=self.current_query,
        )

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

from PySide6.QtWidgets import QWidget

from modules.sessions.service import execute_query
from ui.state.state import get_selected_connection
from ui.utils.layouts import hbox, vbox
from ui.widgets.workspace.sql_editor.sql_editor import SqlEditor
from ui.widgets.workspace.sql_scope import SqlScope


class Workspace(QWidget):

    # =================
    # === VARIABLES ===
    # =================

    # ============
    # === INIT ===
    # ============

    def __init__(self):
        """
        Inicializa el espacio de trabajo.
        """

        super().__init__()

        self._setup_ui()
        self._connect_signals()

    # ================
    # === UI SETUP ===
    # ================

    def _setup_ui(self) -> None:
        """
        Construye la interfaz principal del widget.
        """
        main_layout = hbox()
        self.setLayout(main_layout)

        sql_layout = vbox()
        main_layout.addLayout(sql_layout)

        self.sql_editor = SqlEditor()

        sql_layout.addWidget(self.sql_editor)

    # ================
    # === UI STATE ===
    # ================

    # ==================
    # === UI HELPERS ===
    # ==================

    # ===============
    # === SIGNALS ===
    # ===============

    def _connect_signals(self) -> None:
        self.sql_editor.execute_requested.connect(self._on_execute_requested)

    # ======================
    # === EVENT HANDLERS ===
    # ======================

    def _on_execute_requested(
        self,
        sql: str,
        scope: SqlScope,
    ) -> None:
        execute_query(connection_id=get_selected_connection().id, query=sql)

    # =====================
    # === EVENT HELPERS ===
    # =====================

    # ====================
    # === QT OVERRIDES ===
    # ====================

    # ===================
    # === PRIVATE API ===
    # ===================

    # ==================
    # === PUBLIC API ===
    # ==================

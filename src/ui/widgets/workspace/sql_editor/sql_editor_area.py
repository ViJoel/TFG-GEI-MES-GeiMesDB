from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

from entities.sql_scope import SqlScope
from ui.utils.layouts import vbox
from ui.widgets.workspace.sql_editor.sql_editor import SqlEditor
from ui.widgets.workspace.sql_editor.toolbar import Toolbar


class SqlEditorArea(QWidget):

    # =================
    # === VARIABLES ===
    # =================

    execute_requested = Signal(
        list,
        object,
    )

    # ============
    # === INIT ===
    # ============

    def __init__(
        self,
    ) -> None:

        super().__init__()

        self.setObjectName("sql_editor_area")

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

        layout = vbox(sp=8)

        self.setLayout(layout)

        self.toolbar = Toolbar()
        self.editor = SqlEditor()

        layout.addWidget(self.toolbar)
        layout.addWidget(self.editor)

    # ================
    # === UI STATE ===
    # ================

    # ==================
    # === UI HELPERS ===
    # ==================

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

        self.toolbar.execute_selection_requested.connect(
            lambda: self.editor.execute(SqlScope.SELECTED_TEXT)
        )

        self.toolbar.execute_query_requested.connect(
            lambda: self.editor.execute(SqlScope.ACTUAL_QUERY)
        )

        self.toolbar.execute_script_requested.connect(
            lambda: self.editor.execute(SqlScope.FULL_SCRIPT)
        )

        self.toolbar.undo_requested.connect(self.editor.undo)

        self.toolbar.redo_requested.connect(self.editor.redo)

        # Reemitir hacia el exterior.
        self.editor.execute_requested.connect(self.execute_requested)

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

    # ==================
    # === PUBLIC API ===
    # ==================

    def set_query_text(
        self,
        text: str,
    ) -> None:
        """
        Inserta el texto SQL proporcionado dentro del editor
        en la posición actual del cursor.

        Args:
            text (str):
                Texto a insertar.
        """

        self.editor.insert_query_at_cursor(text)

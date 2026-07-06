from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget

from ui.utils.layouts import hbox
from ui.widgets.workspace.sql_editor.toolbar_button import ToolbarButton
from ui.widgets.workspace.sql_editor.toolbar_separator import ToolbarSeparator


class Toolbar(QWidget):

    # =================
    # === VARIABLES ===
    # =================

    execute_query_requested = Signal()
    execute_script_requested = Signal()
    undo_requested = Signal()
    redo_requested = Signal()

    # ============
    # === INIT ===
    # ============

    def __init__(
        self,
    ) -> None:

        super().__init__()

        self.setObjectName("toolbar")

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

        self.execute_button = ToolbarButton(
            "fa5s.play",
            "execute_query",
            "Execute query",
        )

        self.execute_script_button = ToolbarButton(
            "fa5s.play-circle",
            "execute_script",
            "Execute script",
        )

        self.undo_button = ToolbarButton(
            "fa5s.undo-alt",
            "undo",
            "Undo",
        )

        self.redo_button = ToolbarButton(
            "fa5s.redo-alt",
            "redo",
            "Redo",
        )

        layout = hbox(
            ml=4,
            mt=4,
            mr=4,
            mb=4,
            sp=4,
        )
        self.setLayout(layout)

        layout.addWidget(self.undo_button)
        layout.addWidget(self.redo_button)
        layout.addWidget(ToolbarSeparator())
        layout.addWidget(self.execute_button)
        layout.addWidget(self.execute_script_button)
        layout.addStretch()

        self.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground,
            True,
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

        self.execute_button.clicked.connect(
            self.execute_query_requested,
        )

        self.execute_script_button.clicked.connect(
            self.execute_script_requested,
        )

        self.undo_button.clicked.connect(
            self.undo_requested,
        )

        self.redo_button.clicked.connect(
            self.redo_requested,
        )

from PySide6.QtCore import (
    Qt,
    Signal,
)
from PySide6.QtWidgets import QWidget

from ui.utils.layouts import flow
from ui.widgets.workspace.sql_editor.toolbar_button import ToolbarButton
from ui.widgets.workspace.sql_editor.toolbar_separator import ToolbarSeparator


class Toolbar(QWidget):
    """
    Barra de herramientas del editor SQL.

    Proporciona accesos a las operaciones más habituales y
    expone señales para que el contenedor gestione su lógica.
    """

    # =================
    # === VARIABLES ===
    # =================

    execute_selection_requested = Signal()
    execute_query_requested = Signal()
    execute_script_requested = Signal()
    undo_requested = Signal()
    redo_requested = Signal()
    new_file_requested = Signal()
    open_file_requested = Signal()
    save_file_requested = Signal()
    rename_file_requested = Signal()

    # ============
    # === INIT ===
    # ============

    def __init__(
        self,
    ) -> None:
        """
        Inicializa la barra de herramientas.
        """

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

        self._create_buttons()
        self._set_buttons_tooltips()
        self._build_layout()

        self.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground,
            True,
        )

    # ==================
    # === UI HELPERS ===
    # ==================

    def _create_buttons(
        self,
    ) -> None:
        """
        Crea los botones que componen la barra
        de herramientas.
        """

        self.execute_selection_button = ToolbarButton(
            "fa5s.play",
            "execute_selection",
            self.tr("Execute selection"),
        )

        self.execute_query_button = ToolbarButton(
            "fa5s.play-circle",
            "execute_query",
            self.tr("Execute query"),
        )

        self.execute_script_button = ToolbarButton(
            "mdi.script-text-play",
            "execute_script",
            self.tr("Execute script"),
        )

        self.undo_button = ToolbarButton(
            "fa5s.undo-alt",
            "undo",
            self.tr("Undo"),
        )

        self.redo_button = ToolbarButton(
            "fa5s.redo-alt",
            "redo",
            self.tr("Redo"),
        )

        self.new_button = ToolbarButton(
            "ei.file-new",
            "new_file",
            self.tr("New file"),
        )

        self.open_button = ToolbarButton(
            "fa5s.folder-open",
            "open_file",
            self.tr("Open file"),
        )

        self.save_button = ToolbarButton(
            "fa5s.save",
            "save_file",
            self.tr("Save file"),
        )

        self.rename_button = ToolbarButton(
            "mdi6.rename-box",
            "rename_file",
            self.tr("Rename file"),
        )

    def _set_buttons_tooltips(
        self,
    ) -> None:
        """
        Configura los textos de ayuda mostrados
        al situar el cursor sobre cada botón.
        """

        self.execute_selection_button.setToolTip(
            self.tr(
                "Execute the text selected.<br><br><b>Shortcut:</b> <code>Ctrl + Alt + Enter</code>",
            )
        )

        self.execute_query_button.setToolTip(
            self.tr(
                "Execute the query under the cursor.<br><br><b>Shortcut:</b> <code>Ctrl + Enter</code>",
            )
        )

        self.execute_script_button.setToolTip(
            self.tr(
                "Execute the full script.<br><br><b>Shortcut:</b> <code>Ctrl + Shift + Enter</code>",
            )
        )

        self.undo_button.setToolTip(
            self.tr(
                "Undo action on the text.<br><br><b>Shortcut:</b> <code>Ctrl + Z</code>",
            )
        )

        self.redo_button.setToolTip(
            self.tr(
                "Redo action on the text.<br><br><b>Shortcut:</b> <code>Ctrl + Shift + Z</code>",
            )
        )

        self.new_button.setToolTip(
            self.tr(
                "Create a new file.<br><br><b>Shortcut:</b> <code>Ctrl + N</code>",
            )
        )

        self.open_button.setToolTip(
            self.tr(
                "Open a file from your computer.<br><br><b>Shortcut:</b> <code>Ctrl + O</code>",
            )
        )

        self.save_button.setToolTip(
            self.tr(
                "Save the file changes.<br><br><b>Shortcut:</b> <code>Ctrl + S</code>",
            )
        )

        self.rename_button.setToolTip(
            self.tr(
                "Rename the file.<br><br><b>Shortcut:</b> <code>Ctrl + R</code>",
            )
        )

    def _build_layout(
        self,
    ) -> None:
        """
        Construye la disposición visual de los
        controles de la barra de herramientas.
        """

        layout = flow(
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

        layout.addWidget(self.execute_selection_button)
        layout.addWidget(self.execute_query_button)
        layout.addWidget(self.execute_script_button)

        layout.addWidget(ToolbarSeparator())

        layout.addWidget(self.new_button)
        layout.addWidget(self.open_button)
        layout.addWidget(self.save_button)
        layout.addWidget(self.rename_button)

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

        self.execute_selection_button.clicked.connect(
            self.execute_selection_requested,
        )

        self.execute_query_button.clicked.connect(
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

        self.new_button.clicked.connect(
            self.new_file_requested,
        )

        self.open_button.clicked.connect(
            self.open_file_requested,
        )

        self.save_button.clicked.connect(
            self.save_file_requested,
        )

        self.rename_button.clicked.connect(
            self.rename_file_requested,
        )

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
)

from entities.query_result import QueryResult
from ui.widgets.workspace.results_view.console import Console
from ui.widgets.workspace.results_view.table import Table


class ResultsView(QWidget):

    # =================
    # === VARIABLES ===
    # =================

    # ============
    # === INIT ===
    # ============

    def __init__(self) -> None:
        """
        Inicializa la vista de resultados.
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

        pagelayout = QVBoxLayout()

        toolbar_layout = QHBoxLayout()
        self.left_toolbar_layout = QHBoxLayout()
        self.right_toolbar_layout = QHBoxLayout()

        self.stacklayout = QStackedLayout()

        toolbar_layout.addLayout(self.left_toolbar_layout)
        toolbar_layout.addStretch()
        toolbar_layout.addLayout(self.right_toolbar_layout)

        pagelayout.addLayout(toolbar_layout)
        pagelayout.addLayout(self.stacklayout)

        self._create_tab_buttons()
        self._create_cell_buttons()
        self._create_tabs()

        self.setLayout(pagelayout)

    # ================
    # === UI STATE ===
    # ================

    def show_console(self):
        self.stacklayout.setCurrentWidget(self.console)

    def show_table(self):
        self.stacklayout.setCurrentWidget(self.table)

    def show_result(
        self,
        result: QueryResult,
    ) -> None:

        self.console.clear_output()
        self.console.write(result.console_output)

        if result.result_set is None:

            self.show_console()

        else:

            self.table.set_result_set(result.result_set)

            self.show_table()

    # ==================
    # === UI HELPERS ===
    # ==================

    @staticmethod
    def _create_button(text: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Fixed,
        )
        return btn

    def _create_tab_buttons(self) -> None:

        self.console_button = self._create_button("Console")
        self.left_toolbar_layout.addWidget(self.console_button)

        self.table_button = self._create_button("Table")
        self.left_toolbar_layout.addWidget(self.table_button)

    def _create_cell_buttons(self) -> None:

        self.save_button = self._create_button("Save")
        self.right_toolbar_layout.addWidget(self.save_button)

        self.discard_button = self._create_button("Discard")
        self.right_toolbar_layout.addWidget(self.discard_button)

    def _create_tabs(self) -> None:
        self.console = Console()
        self.stacklayout.addWidget(self.console)

        self.table = Table()
        self.stacklayout.addWidget(self.table)

    # ===============
    # === SIGNALS ===
    # ===============

    def _connect_signals(self) -> None:
        """
        Conecta señales de widgets
        con sus handlers correspondientes.
        """

        self.console_button.pressed.connect(self.show_console)
        self.table_button.pressed.connect(self.show_table)
        self.discard_button.clicked.connect(self.table.discard_changes)

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

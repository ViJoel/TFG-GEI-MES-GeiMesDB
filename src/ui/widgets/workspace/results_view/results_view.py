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
        button_layout = QHBoxLayout()
        self.stacklayout = QStackedLayout()

        pagelayout.addLayout(button_layout)
        pagelayout.addLayout(self.stacklayout)

        # Añadimos los botones de pestañas
        self.console_button = self._create_button("Console")
        button_layout.addWidget(self.console_button)

        self.table_button = self._create_button("Table")
        button_layout.addWidget(self.table_button)

        # Añadimos las pestañas
        self.console = Console()
        self.stacklayout.addWidget(self.console)

        self.table = QLabel("Table")
        self.stacklayout.addWidget(self.table)

        self.setLayout(pagelayout)

    # ================
    # === UI STATE ===
    # ================

    def show_console(self):
        self.stacklayout.setCurrentIndex(0)

    def show_table(self):
        self.stacklayout.setCurrentIndex(1)

    def show_result(
        self,
        result: QueryResult,
    ) -> None:

        self.console.clear_output()
        self.console.write(result.console_output)

        if result.result_set is None:

            self.show_console()

        else:

            # self.table.set_result_set(result.result_set)

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

from PySide6.QtWidgets import QTableView

from entities.query_result import ResultSet
from ui.widgets.workspace.results_view.result_table_model import ResultTableModel


class Table(QTableView):

    # =================
    # === VARIABLES ===
    # =================

    # ============
    # === INIT ===
    # ============

    def __init__(self) -> None:

        super().__init__()

        self._setup_ui()

    # ================
    # === UI SETUP ===
    # ================

    def _setup_ui(self) -> None:
        """
        Construye la interfaz principal del widget.
        """

        pass

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
        """
        Conecta señales de widgets
        con sus handlers correspondientes.
        """

        pass

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

    def set_result_set(
        self,
        result_set: ResultSet,
    ) -> None:

        model = ResultTableModel(result_set)

        self.setModel(model)

    def discard_changes(
        self,
    ) -> None:

        self.model().discard_changes()

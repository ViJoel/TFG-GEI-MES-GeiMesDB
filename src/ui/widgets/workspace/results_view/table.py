from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QTableView,
)

from entities.query_result import ResultSet
from ui.widgets.workspace.results_view.result_table_model import ResultTableModel


class Table(QTableView):

    # =================
    # === VARIABLES ===
    # =================

    data_changed = Signal(bool)

    # ============
    # === INIT ===
    # ============

    def __init__(self) -> None:

        super().__init__()

        self.model: ResultTableModel | None = None

    # ==================
    # === PUBLIC API ===
    # ==================

    def set_result_set(
        self,
        result_set: ResultSet,
    ) -> None:

        self.model = ResultTableModel(result_set)

        self.model.state_changed.connect(self.data_changed)

        self.setModel(self.model)

    def discard_changes(
        self,
    ) -> None:

        if self.model is not None:
            self.model.discard_changes()

    def set_editable(
        self,
        editable: bool,
    ) -> None:

        if editable:

            self.setEditTriggers(
                QAbstractItemView.EditTrigger.DoubleClicked
                | QAbstractItemView.EditTrigger.EditKeyPressed
            )

        else:

            self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

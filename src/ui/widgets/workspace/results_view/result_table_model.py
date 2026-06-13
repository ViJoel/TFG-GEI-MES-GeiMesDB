from copy import deepcopy
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from PySide6.QtCore import QAbstractTableModel, Qt
from PySide6.QtGui import QColor

from entities.query_result import ResultSet


class ResultTableModel(QAbstractTableModel):

    # =================
    # === VARIABLES ===
    # =================

    # ============
    # === INIT ===
    # ============

    def __init__(
        self,
        result_set: ResultSet,
    ) -> None:

        super().__init__()

        self.result_set = result_set
        self.original_result_set = deepcopy(result_set)
        self.modified_cells: set[tuple[int, int]] = set()

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

    def rowCount(
        self,
        parent=None,
    ) -> int:

        return len(self.result_set.rows)

    def columnCount(
        self,
        parent=None,
    ) -> int:

        return len(self.result_set.columns)

    def data(
        self,
        index,
        role,
    ):

        row = index.row()
        column = index.column()

        if role in (
            Qt.DisplayRole,
            Qt.EditRole,
        ):

            return self.result_set.rows[row][column]

        if role == Qt.BackgroundRole:

            if (row, column) in self.modified_cells:

                return QColor("red")

    def headerData(
        self,
        section,
        orientation,
        role,
    ):

        if orientation == Qt.Horizontal and role == Qt.DisplayRole:

            return self.result_set.columns[section]

    def flags(
        self,
        index,
    ):

        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    def setData(
        self,
        index,
        value,
        role,
    ):
        if role != Qt.EditRole:
            return False

        row = index.row()
        column = index.column()

        original_value = self.original_result_set.rows[row][column]

        new_value = self._convert_value(
            column=column,
            value=value,
        )

        print(
            f"Old: {original_value!r} ({type(original_value).__name__}) "
            f"-> New: {new_value!r} ({type(new_value).__name__})"
        )

        self._modify_cell_value(
            row=row,
            column=column,
            original_value=original_value,
            new_value=new_value,
        )

        self.dataChanged.emit(
            index,
            index,
        )

        return True

    # ===================
    # === PRIVATE API ===
    # ===================

    def _modify_cell_value(
        self,
        row: int,
        column: int,
        original_value: Any,
        new_value: Any,
    ):

        self.result_set.rows[row][column] = new_value

        if new_value == original_value:
            self.modified_cells.discard((row, column))
        else:
            self.modified_cells.add((row, column))

    def _convert_value(
        self,
        column: int,
        value: str,
    ) -> Any:

        try:

            column_type = self.result_set.columns_types[column]

            if value == "":
                return None

            if column_type is int:
                return int(value)

            if column_type is float:
                return float(value)

            if column_type is str:
                return value

            if column_type is bool:
                return value.lower() in (
                    "true",
                    "1",
                    "yes",
                )

            if column_type is Decimal:
                return Decimal(value)

            if column_type is date:
                return date.fromisoformat(value)

            if column_type is datetime:
                return datetime.fromisoformat(value)

            return value

        except (
            ValueError,
            TypeError,
        ):

            return value

    # ==================
    # === PUBLIC API ===
    # ==================

    def discard_changes(
        self,
    ) -> None:

        self.result_set.columns = deepcopy(self.original_result_set.columns)
        self.result_set.rows = deepcopy(self.original_result_set.rows)

        self.modified_cells.clear()

        self.layoutChanged.emit()

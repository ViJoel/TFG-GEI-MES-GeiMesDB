from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QTableView,
)

from entities.query_result import ResultSet
from ui.widgets.workspace.results_view.result_table_model import ResultTableModel


class Table(QTableView):
    """
    Widget visual encargado de mostrar resultados
    de consultas en formato tabular.

    Permite visualizar la información obtenida y
    habilitar o restringir su edición en función
    de las características del conjunto de resultados.
    """

    # =================
    # === VARIABLES ===
    # =================

    data_changed = Signal(bool)

    # ============
    # === INIT ===
    # ============

    def __init__(
        self,
    ) -> None:
        """
        Inicializa la tabla de resultados.
        """

        super().__init__()

        self.setObjectName("table")

        self._setup_ui()

        self.model: ResultTableModel | None = None

    # ================
    # === UI SETUP ===
    # ================

    def _setup_ui(
        self,
    ) -> None:
        """
        Construye la interfaz principal del widget.
        """

        self.setCornerButtonEnabled(False)

        self.verticalHeader().hide()

        self.setAlternatingRowColors(True)

        self.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows,
        )

        self.horizontalHeader().setSectionsClickable(False)

        self.horizontalHeader().setHighlightSections(False)

        self.setSortingEnabled(False)

        self.setShowGrid(True)

        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    # ==================
    # === PUBLIC API ===
    # ==================

    def set_result_set(
        self,
        result_set: ResultSet,
    ) -> None:
        """
        Asigna un conjunto de resultados a la
        tabla.

        Args:
            result_set (ResultSet):
                Conjunto de resultados que se
                mostrará en la tabla.
        """

        self.model = ResultTableModel(result_set)

        self.model.state_changed.connect(self.data_changed)

        self.setModel(self.model)

    def discard_changes(
        self,
    ) -> None:
        """
        Descarta los cambios pendientes realizados
        sobre los datos mostrados.
        """

        if self.model is not None:
            self.model.discard_changes()

    def set_editable(
        self,
        editable: bool,
    ) -> None:
        """
        Habilita o deshabilita la edición de las
        celdas de la tabla.

        Args:
            editable (bool):
                Indica si las celdas deben poder
                editarse.
        """

        if editable:

            self.setEditTriggers(
                QAbstractItemView.EditTrigger.DoubleClicked
                | QAbstractItemView.EditTrigger.EditKeyPressed
            )

        else:

            self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
)

from entities.query_result import QueryResult
from entities.script_result import ScriptResult
from ui.widgets.workspace.results_view.console import Console
from ui.widgets.workspace.results_view.table import Table


class ResultsView(QWidget):
    """
    Widget encargado de mostrar los resultados
    de la ejecuciónconsultas y scripts.

    Permite alternar entre una vista tabular y una
    vista de consola, así como gestionar acciones
    relacionadas con la persistencia de cambios.
    """

    # =================
    # === VARIABLES ===
    # =================

    save_requested = Signal()

    # ============
    # === INIT ===
    # ============

    def __init__(
        self,
    ) -> None:
        """
        Inicializa la vista de resultados.
        """

        super().__init__()

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
        self._create_action_buttons()
        self._create_tabs()

        self.setLayout(pagelayout)

    # ================
    # === UI STATE ===
    # ================

    def show_console(
        self,
    ) -> None:
        """
        Muestra la vista de consola.
        """

        self.stacklayout.setCurrentWidget(self.console)

    def show_table(
        self,
    ) -> None:
        """
        Muestra la vista tabular.
        """

        self.stacklayout.setCurrentWidget(self.table)

    def show_result(
        self,
        result: QueryResult,
        script_result: ScriptResult,
        is_script: bool,
    ) -> None:
        """
        Muestra el resultado de una ejecución.

        Args:
            result (QueryResult):
                Resultado de la consulta ejecutada.

            script_result (ScriptResult):
                Resultado obtenido tras la ejecución
                del script.

            is_script (bool):
                Indica si el resultado corresponde a
                la ejecución de un script.
        """

        self.console.clear_output()

        if not is_script:

            self.console.write(
                result.console_output,
            )

            # Sentencia DQL
            if result.result_set is not None:

                self.table.set_result_set(
                    result.result_set,
                )

                self.show_table()

                self.set_tab_buttons_state(
                    True,
                )

                return

        else:

            self.console.show_script_result(
                script_result,
            )

        # Resultado de script o Sentencia DDL o DML
        self.show_console()

        self.set_tab_buttons_state(
            False,
        )

    # ==================
    # === UI HELPERS ===
    # ==================

    @staticmethod
    def _create_button(
        text: str,
    ) -> QPushButton:
        """
        Crea un botón con tamaño fijo.

        Args:
            text (str):
                Texto que se mostrará en el botón.

        Returns:
            QPushButton:
                Botón creado.
        """

        btn = QPushButton(text)

        btn.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Fixed,
        )

        return btn

    def _create_tab_buttons(
        self,
    ) -> None:
        """
        Crea los botones utilizados para alternar
        entre las distintas vistas.
        """

        self.console_button = self._create_button("Console")
        self.left_toolbar_layout.addWidget(self.console_button)

        self.table_button = self._create_button("Table")
        self.left_toolbar_layout.addWidget(self.table_button)

    def _create_action_buttons(
        self,
    ) -> None:
        """
        Crea los botones asociados a las acciones
        disponibles sobre los resultados.
        """

        self.save_button = self._create_button("Save")
        self.right_toolbar_layout.addWidget(self.save_button)

        self.discard_button = self._create_button("Discard")
        self.right_toolbar_layout.addWidget(self.discard_button)

        self._set_action_buttons_initial_state()

    def _create_tabs(
        self,
    ) -> None:
        """
        Crea las vistas disponibles para mostrar los
        resultados.
        """

        self.console = Console()
        self.stacklayout.addWidget(self.console)

        self.table = Table()
        self.stacklayout.addWidget(self.table)

    def _set_action_buttons_initial_state(
        self,
    ) -> None:
        """
        Establece el estado inicial de los botones de
        acción.
        """

        self.save_button.setEnabled(False)
        self.discard_button.setEnabled(False)

    # ===============
    # === SIGNALS ===
    # ===============

    def _connect_signals(self) -> None:
        """
        Conecta señales de widgets
        con sus handlers correspondientes.
        """

        self.console_button.pressed.connect(
            self.show_console,
        )

        self.table_button.pressed.connect(
            self.show_table,
        )

        self.save_button.clicked.connect(
            self.save_requested,
        )

        self.discard_button.clicked.connect(
            self.table.discard_changes,
        )

        self.table.data_changed.connect(
            self.set_action_buttons_state,
        )

    # ==================
    # === PUBLIC API ===
    # ==================

    def set_action_buttons_state(
        self,
        state: bool,
    ) -> None:
        """
        Habilita o deshabilita los botones de acción.

        Args:
            state (bool):
                Estado que se aplicará a los botones.
        """

        self.save_button.setEnabled(state)
        self.discard_button.setEnabled(state)

    def set_tab_buttons_state(
        self,
        state: bool,
    ) -> None:
        """
        Habilita o deshabilita los botones de cambio
        de vista.

        Args:
            state (bool):
                Estado que se aplicará a los botones.
        """

        self.console_button.setEnabled(state)
        self.table_button.setEnabled(state)

    def set_editable(
        self,
        editable: bool,
    ) -> None:
        """
        Configura si los datos mostrados pueden ser
        editados.

        Args:
            editable (bool):
                Indica si debe permitirse la edición
                de los resultados.
        """

        self.table.set_editable(editable)

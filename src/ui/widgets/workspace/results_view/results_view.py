from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QPushButton,
    QSizePolicy,
    QStackedLayout,
    QWidget,
)

from entities.connection import Connection
from entities.message_type import MessageType
from entities.queries_history_entry import QueriesHistoryEntry
from entities.query_result import QueryResult
from entities.script_result import ScriptResult
from ui.app.app_actions import notify
from ui.utils.layouts import (
    hbox,
    vbox,
)
from ui.widgets.dialogs.confirmation_dialog import ConfirmationDialog
from ui.widgets.workspace.results_view.connection_queries_history import (
    ConnectionQueriesHistory,
)
from ui.widgets.workspace.results_view.console import Console
from ui.widgets.workspace.results_view.session_queries_history import (
    SessionQueriesHistory,
)
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
    query_selected_from_session_queries_history = Signal(str)

    # ============
    # === INIT ===
    # ============

    def __init__(
        self,
        connection: Connection,
    ) -> None:
        """
        Inicializa la vista de resultados.
        """

        super().__init__()

        self.connection = connection

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

        pagelayout = vbox(mt=12)

        toolbar_layout = hbox(mb=8)
        self.left_toolbar_layout = hbox()
        self.right_toolbar_layout = hbox()

        self.left_toolbar_layout.setSpacing(4)
        self.right_toolbar_layout.setSpacing(4)

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

    def _show_session_queries_history(
        self,
    ) -> None:
        """
        Muestra la vista del historial de consultas de la sesión.
        """

        self.stacklayout.setCurrentWidget(self.session_queries_history)

    def _show_connection_queries_history(
        self,
    ) -> None:
        """
        Muestra la vista del historial de consultas de la conexión.
        """

        self.stacklayout.setCurrentWidget(self.connection_queries_history)

    # ==================
    # === UI HELPERS ===
    # ==================

    @staticmethod
    def _create_button(
        text: str,
        button_type: str,
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

        btn.setProperty("type", button_type)

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

        self.console_button = self._create_button(
            "Console",
            "primary",
        )

        self.left_toolbar_layout.addWidget(self.console_button)

        self.table_button = self._create_button(
            "Table",
            "primary",
        )

        self.left_toolbar_layout.addWidget(self.table_button)

        self.session_queries_history_button = self._create_button(
            "Session queries history",
            "primary",
        )

        self.left_toolbar_layout.addWidget(self.session_queries_history_button)

        self.connection_queries_history_button = self._create_button(
            "Connection queries history",
            "primary",
        )

        self.left_toolbar_layout.addWidget(self.connection_queries_history_button)

    def _create_action_buttons(
        self,
    ) -> None:
        """
        Crea los botones asociados a las acciones
        disponibles sobre los resultados.
        """

        self.save_button = self._create_button(
            "Save",
            "secondary",
        )

        self.right_toolbar_layout.addWidget(self.save_button)

        self.discard_button = self._create_button(
            "Discard",
            "secondary",
        )

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

        self.session_queries_history = SessionQueriesHistory()
        self.stacklayout.addWidget(self.session_queries_history)

        self.connection_queries_history = ConnectionQueriesHistory(
            connection=self.connection
        )
        self.stacklayout.addWidget(self.connection_queries_history)

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

        self.session_queries_history_button.pressed.connect(
            self._show_session_queries_history
        )

        self.connection_queries_history_button.pressed.connect(
            self._show_connection_queries_history
        )

        self.save_button.clicked.connect(
            self._on_save_button_clicked,
        )

        self.discard_button.clicked.connect(
            self._on_discard_button_clicked,
        )

        self.table.data_changed.connect(
            self.set_action_buttons_state,
        )

        self.session_queries_history.query_selected.connect(
            self.query_selected_from_session_queries_history.emit
        )

    # ======================
    # === EVENT HANDLERS ===
    # ======================

    def _on_save_button_clicked(
        self,
    ) -> None:

        dialog = ConfirmationDialog(
            title="Save changes",
            message="Are you sure you want to save the changes?",
            parent=self,
        )

        dialog.confirmed.connect(
            self._save_changes,
        )

        dialog.exec()

    def _on_discard_button_clicked(
        self,
    ) -> None:

        dialog = ConfirmationDialog(
            title="Discard changes",
            message="Are you sure you want to discard the changes?",
            parent=self,
        )

        dialog.confirmed.connect(
            self._discard_changes,
        )

        dialog.exec()

    # =====================
    # === EVENT HELPERS ===
    # =====================

    def _save_changes(
        self,
    ) -> None:

        self.save_requested.emit()

        notify(
            MessageType.SUCCESS,
            "Changes saved",
        )

    def _discard_changes(
        self,
    ) -> None:

        self.table.discard_changes()

        notify(
            MessageType.INFO,
            "Changes discarted",
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
                MessageType.DEFAULT,
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

    def write_message(
        self,
        text: str,
        message_type: MessageType = MessageType.DEFAULT,
    ) -> None:
        """
        Escribe un mensaje en la consola.

        Args:
            text (str):
                Texto que se mostrará en la consola.

            message_type (MessageType):
                Tipo de mensaje que determina el
                color con el que se mostrará
                el texto.
        """

        self.console.clear_output()

        self.console.write(
            text=text,
            message_type=message_type,
        )

    def add_entry_to_session_queries_history(
        self,
        entry: QueriesHistoryEntry,
        row: int | None = None,
    ) -> None:
        """
        Añade una nueva entrada al historial
        de consultas de la sesión.

        Args:
            entry (QueriesHistoryEntry):
                Nueva entrada que se añadirá al historial.

            row (int | None):
                Posición donde insertar la entrada.

                - Si se especifica, la entrada se inserta
                en dicha posición.
                - Si es `None`, la entrada se añade al
                final del historial.
        """

        self.session_queries_history.add_entry(
            entry,
            row,
        )

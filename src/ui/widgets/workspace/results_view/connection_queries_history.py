import logging
from datetime import datetime

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QDateEdit,
    QPushButton,
    QWidget,
)

from entities.connection import Connection
from entities.message_type import MessageType
from log.app_logger import get_logger
from modules.queries_history.service import get_queries_history
from ui.app.app_actions import notify
from ui.app.app_context import AppContext
from ui.app.worker_error import WorkerError
from ui.utils.layouts import (
    hbox,
    vbox,
)
from ui.widgets.workspace.results_view.console import Console

logger = get_logger(__name__)


class ConnectionQueriesHistory(QWidget):

    # ============
    # === INIT ===
    # ============

    def __init__(
        self,
        connection: Connection,
    ) -> None:
        """
        Inicializa el historial de consultas
        de la conexión.

        Args:
            connection (Connection):
                Conexión de la que se cargará el historial.
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

        layout = hbox(sp=20)
        self.setLayout(layout)

        inputs_layout = vbox(sp=4)
        layout.addLayout(inputs_layout)

        # Inputs de fechas con calendario flotante
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(
            QDate.currentDate().addDays(-7)
        )  # Por defecto, hace una semana
        inputs_layout.addWidget(self.start_date)

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())  # Por defecto, hoy
        inputs_layout.addWidget(self.end_date)

        # Botón de acción
        self.btn_filter = QPushButton("Filtrar")
        inputs_layout.addWidget(self.btn_filter)

        # Consola de display
        self.console = Console()
        layout.addWidget(self.console)

        self._load_history()

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

        self.btn_filter.clicked.connect(self._load_history)

    # ===================
    # === PRIVATE API ===
    # ===================

    def _load_history(
        self,
    ) -> None:
        """
        Carga el historial de consultas de
        la conexión filtrado por fechas.
        """

        notify(
            MessageType.WARNING,
            "Loading history...",
        )

        start_date = self.start_date.dateTime().toPython()

        end_date = (
            self.end_date.dateTime()
            .toPython()
            .replace(
                hour=23,
                minute=59,
                second=59,
                microsecond=999999,
            )
        )

        self.btn_filter.setEnabled(False)

        AppContext.get_task_manager().run(
            get_queries_history,
            connection=self.connection,
            start=start_date,
            end=end_date,
            on_success=self._on_load_history_success,
            on_error=self._on_load_history_error,
            on_finished=lambda: self.btn_filter.setEnabled(True),
        )

    def _on_load_history_success(
        self,
        history,
    ) -> None:

        self.console.clear_output()

        total_entries = len(history)

        for index, entry in enumerate(history):

            self.console.write(
                "[" + entry.executed_at.strftime("%Y/%m/%d - %H:%M:%S") + "]\n\n",
                MessageType.DISABLED,
            )

            self.console.write(
                entry.query,
                MessageType.DEFAULT,
            )

            if index < total_entries - 1:

                self.console.write(
                    "\n\n" + "-" * 100 + "\n\n",
                    MessageType.INFO,
                )

        notify(
            MessageType.SUCCESS,
            "History loaded.",
        )

    def _on_load_history_error(
        self,
        error: WorkerError,
    ) -> None:

        logger.error(error.traceback)

        notify(
            MessageType.ERROR,
            "History load failed.",
        )

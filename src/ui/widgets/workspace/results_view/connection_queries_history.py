from PySide6.QtCore import (
    QDate,
    Qt,
)
from PySide6.QtWidgets import (
    QDateEdit,
    QLabel,
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
from ui.translations.translation_manager import TranslationManager
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

        layout = hbox(sp=8)
        self.setLayout(layout)

        inputs_widget = QWidget()
        inputs_widget.setObjectName("connection_queries_history_inputs")
        inputs_widget.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground,
            True,
        )
        layout.addWidget(inputs_widget)

        inputs_layout = vbox(
            ml=20,
            mt=20,
            mr=20,
            mb=20,
            sp=16,
        )
        inputs_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        )
        inputs_widget.setLayout(inputs_layout)

        # Inputs de fechas con calendario flotante
        start_widget, self.start_date_label, self.start_date = self._create_date_input()
        self.start_date.setDate(QDate.currentDate().addDays(-7))
        inputs_layout.addWidget(start_widget)

        end_widget, self.end_date_label, self.end_date = self._create_date_input()
        self.end_date.setDate(QDate.currentDate())
        inputs_layout.addWidget(end_widget)

        # Espaciado entre los inputs y el botón
        inputs_layout.addSpacing(16)

        # Botón de acción
        self.filter_button = QPushButton()
        self.filter_button.setProperty(
            "type",
            "accent",
        )
        inputs_layout.addWidget(self.filter_button)

        # Consola de display
        self.console = Console()
        layout.addWidget(self.console)

        self._retranslate_ui()

        self._load_history()

    def _retranslate_ui(
        self,
    ) -> None:
        """
        Actualiza todos los textos traducibles del widget.

        Los textos se generan en el momento de la llamada
        utilizando el traductor activo de Qt, permitiendo
        refrescar la interfaz después de cambiar el idioma
        de la aplicación.
        """

        self.start_date_label.setText(
            self.tr("Start date"),
        )

        self.end_date_label.setText(
            self.tr("End date"),
        )

        self.filter_button.setText(
            self.tr("Filter"),
        )

    # ==================
    # === UI HELPERS ===
    # ==================

    def _create_date_input(
        self,
    ) -> tuple[QWidget, QLabel, QDateEdit]:
        """
        Crea un campo de fecha compuesto por
        un label y un QDateEdit.

        Returns:
            tuple[QWidget, QLabel, QDateEdit]:
                Contenedor del campo, label del
                campo y el QDateEdit asociado.
        """

        widget = QWidget()
        widget.setObjectName("connection_queries_history_date")
        widget.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground,
            True,
        )

        layout = vbox(sp=4)
        widget.setLayout(layout)

        label = QLabel()
        label.setObjectName("connection_queries_history_date_input_label")
        layout.addWidget(label)

        date_input = QDateEdit()
        date_input.setObjectName("connection_queries_history_date_input")
        date_input.setCalendarPopup(True)
        date_input.setDisplayFormat("dd/MM/yyyy")
        layout.addWidget(date_input)

        calendar = date_input.calendarWidget()
        calendar.setMinimumSize(360, 300)

        return widget, label, date_input

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

        self.filter_button.clicked.connect(
            self._load_history,
        )

        self.start_date.dateChanged.connect(
            self._on_start_date_changed,
        )

        TranslationManager.events().language_changed.connect(
            self._retranslate_ui,
        )

    # ======================
    # === EVENT HANDLERS ===
    # ======================

    def _on_start_date_changed(
        self,
        date: QDate,
    ) -> None:
        """
        Actualiza la fecha mínima del campo
        de fecha final.

        Si la fecha final actual queda por
        debajo del nuevo mínimo, también se
        ajusta automáticamente.
        """

        self.end_date.setMinimumDate(date)

        if self.end_date.date() < date:
            self.end_date.setDate(date)

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
            self.tr("Loading history..."),
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

        self.filter_button.setEnabled(False)

        AppContext.get_task_manager().run(
            get_queries_history,
            connection=self.connection,
            start=start_date,
            end=end_date,
            on_success=self._on_load_history_success,
            on_error=self._on_load_history_error,
            on_finished=lambda: self.filter_button.setEnabled(True),
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
            self.tr("History loaded."),
        )

    def _on_load_history_error(
        self,
        error: WorkerError,
    ) -> None:

        logger.error(error.traceback)

        notify(
            MessageType.ERROR,
            self.tr("History load failed."),
        )

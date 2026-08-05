from datetime import datetime
from unittest.mock import (
    MagicMock,
    patch,
)

import pytest
from PySide6.QtCore import (
    QDate,
    Qt,
)

from entities.connection import Connection
from entities.driver import Driver
from entities.message_type import MessageType
from ui.widgets.workspace.results_view.connection_queries_history import (
    ConnectionQueriesHistory,
)

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture(autouse=True)
def patch_dependencies():
    """
    Evita llamadas externas durante la creación del widget.
    """

    task_manager = MagicMock()

    task_manager.run.side_effect = lambda *args, **kwargs: (kwargs["on_finished"]())

    with patch(
        "ui.widgets.workspace.results_view.connection_queries_history.notify"
    ), patch(
        "ui.widgets.workspace.results_view.connection_queries_history.get_queries_history",
    ), patch(
        "ui.widgets.workspace.results_view.connection_queries_history.AppContext.get_task_manager",
        return_value=task_manager,
    ):
        yield


@pytest.fixture
def mock_connection():
    return Connection(
        name="Test Connection",
        driver=Driver.POSTGRESQL,
        host="localhost",
        port=5432,
        database="test_db",
        username="admin",
        password="password",
    )


@pytest.fixture
def history_widget(qtbot, mock_connection):
    widget = ConnectionQueriesHistory(
        connection=mock_connection,
    )

    qtbot.addWidget(widget)

    return widget


# =============================================================================
# UI SETUP
# =============================================================================


def test_create_date_input_creates_widget(history_widget):
    """
    Verifica creación de input de fecha.
    """

    widget, label, date_input = history_widget._create_date_input()

    assert widget.objectName() == ("connection_queries_history_date")

    assert label.objectName() == ("connection_queries_history_date_input_label")

    assert label.text() == ""

    assert date_input.objectName() == ("connection_queries_history_date_input")

    assert date_input.calendarPopup() is True

    assert date_input.displayFormat() == "dd/MM/yyyy"


# =============================================================================
# DATE HANDLING
# =============================================================================


def test_on_start_date_changed_updates_minimum_date(history_widget):
    """
    Verifica que cambia la fecha mínima del final.
    """

    new_date = QDate(2025, 1, 10)

    history_widget.end_date.setMinimumDate = MagicMock()
    history_widget.end_date.date = MagicMock(return_value=QDate(2025, 1, 20))

    history_widget._on_start_date_changed(new_date)

    history_widget.end_date.setMinimumDate.assert_called_once_with(new_date)


def test_on_start_date_changed_adjusts_end_date_if_lower(history_widget):
    """
    Verifica que fuerza la fecha final si es menor.
    """

    new_date = QDate(2025, 1, 10)

    history_widget.end_date = MagicMock()

    history_widget.end_date.date.return_value = QDate(
        2025,
        1,
        1,
    )

    history_widget._on_start_date_changed(new_date)

    history_widget.end_date.setMinimumDate.assert_called_once_with(new_date)

    history_widget.end_date.setDate.assert_called_once_with(new_date)


def test_on_start_date_changed_does_not_adjust_end_date(history_widget):
    """
    Verifica que no cambia fecha final si ya es válida.
    """

    new_date = QDate(2025, 1, 10)

    history_widget.end_date = MagicMock()

    history_widget.end_date.date.return_value = QDate(
        2025,
        1,
        20,
    )

    history_widget._on_start_date_changed(new_date)

    history_widget.end_date.setMinimumDate.assert_called_once_with(new_date)

    history_widget.end_date.setDate.assert_not_called()


# =============================================================================
# LOAD HISTORY
# =============================================================================


def test_load_history_disables_button_and_runs_task(
    history_widget,
):
    """
    Verifica que carga historial mediante TaskManager.
    """

    task_manager = MagicMock()

    with patch(
        "ui.widgets.workspace.results_view.connection_queries_history.AppContext.get_task_manager",
        return_value=task_manager,
    ):

        history_widget._load_history()

    history_widget.filter_button.isEnabled()

    task_manager.run.assert_called_once()

    args = task_manager.run.call_args.kwargs

    assert args["connection"] == history_widget.connection
    assert "start" in args
    assert "end" in args
    assert "on_success" in args
    assert "on_error" in args
    assert "on_finished" in args


# =============================================================================
# LOAD SUCCESS
# =============================================================================


def test_on_load_history_success_with_empty_history(
    history_widget,
):
    """
    Verifica éxito sin resultados.
    """

    history_widget.console = MagicMock()

    with patch(
        "ui.widgets.workspace.results_view.connection_queries_history.notify"
    ) as notify_mock:

        history_widget._on_load_history_success([])

    history_widget.console.clear_output.assert_called_once()

    notify_mock.assert_called_once_with(
        MessageType.SUCCESS,
        history_widget.tr("History loaded."),
    )


def test_on_load_history_success_writes_entries(
    history_widget,
):
    """
    Verifica impresión de entradas del historial.
    """

    history_widget.console = MagicMock()

    entry1 = MagicMock()
    entry1.executed_at = datetime(
        2025,
        1,
        1,
        12,
        30,
    )
    entry1.query = "SELECT 1"

    entry2 = MagicMock()
    entry2.executed_at = datetime(
        2025,
        1,
        2,
        10,
        0,
    )
    entry2.query = "SELECT 2"

    history_widget._on_load_history_success(
        [
            entry1,
            entry2,
        ]
    )

    assert history_widget.console.write.call_count == 5


# =============================================================================
# LOAD ERROR
# =============================================================================


def test_on_load_history_error_logs_and_notifies(
    history_widget,
):
    """
    Verifica tratamiento de error.
    """

    error = MagicMock()
    error.traceback = "traceback"

    with patch(
        "ui.widgets.workspace.results_view.connection_queries_history.logger.error"
    ) as logger_mock, patch(
        "ui.widgets.workspace.results_view.connection_queries_history.notify"
    ) as notify_mock:

        history_widget._on_load_history_error(
            error,
        )

    logger_mock.assert_called_once_with("traceback")

    notify_mock.assert_called_once_with(
        MessageType.ERROR,
        history_widget.tr("History load failed."),
    )


# =============================================================================
# SIGNALS
# =============================================================================


def test_filter_button_connected_to_load_history(
    history_widget,
    qtbot,
):
    """
    Verifica que pulsar el botón ejecuta la carga.
    """

    called = False

    def fake_load_history():
        nonlocal called
        called = True

    history_widget.filter_button.clicked.disconnect()

    history_widget.filter_button.clicked.connect(fake_load_history)

    qtbot.mouseClick(
        history_widget.filter_button,
        Qt.MouseButton.LeftButton,
    )

    assert called is True


# =============================================================================
# INTERNATIONALIZATION
# =============================================================================


def test_retranslate_ui_updates_all_translatable_texts(
    history_widget,
):
    """
    Verifica que la interfaz actualiza correctamente todos
    los textos traducibles del widget.
    """

    history_widget._retranslate_ui()

    assert history_widget.start_date_label.text() == history_widget.tr("Start date")

    assert history_widget.end_date_label.text() == history_widget.tr("End date")

    assert history_widget.filter_button.text() == history_widget.tr("Filter")

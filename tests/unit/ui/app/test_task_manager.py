from unittest.mock import MagicMock

from PySide6.QtCore import QThreadPool

from ui.app.task_manager import TaskManager
from ui.app.worker import Worker

# =============================================================================
# __init__
# =============================================================================


def test_task_manager_init(monkeypatch):
    """
    Verifica que el TaskManager obtiene el pool global
    y crea el registro de workers activos.
    """

    pool = MagicMock()

    monkeypatch.setattr(
        QThreadPool,
        "globalInstance",
        MagicMock(return_value=pool),
    )

    manager = TaskManager()

    assert manager._pool is pool
    assert manager._workers == set()


# =============================================================================
# run
# =============================================================================


def test_task_manager_run(monkeypatch):
    """
    Verifica que run crea un Worker, registra los
    callbacks, lo envía al pool y elimina la referencia
    al finalizar.
    """

    pool = MagicMock()

    monkeypatch.setattr(
        QThreadPool,
        "globalInstance",
        MagicMock(return_value=pool),
    )

    manager = TaskManager()

    success = MagicMock()
    error = MagicMock()
    finished = MagicMock()

    worker = manager.run(
        lambda: 123,
        on_success=success,
        on_error=error,
        on_finished=finished,
    )

    assert isinstance(worker, Worker)

    assert worker in manager._workers

    pool.start.assert_called_once_with(worker)

    # Simula la finalización del worker.
    worker.signals.finished.emit()

    finished.assert_called_once()

    assert worker not in manager._workers


def test_task_manager_run_without_callbacks(monkeypatch):
    """
    Verifica que run funciona correctamente cuando
    no se proporcionan callbacks.
    """

    pool = MagicMock()

    monkeypatch.setattr(
        QThreadPool,
        "globalInstance",
        MagicMock(return_value=pool),
    )

    manager = TaskManager()

    worker = manager.run(lambda: None)

    assert worker in manager._workers

    pool.start.assert_called_once_with(worker)

    # La limpieza debe seguir funcionando.
    worker.signals.finished.emit()

    assert worker not in manager._workers

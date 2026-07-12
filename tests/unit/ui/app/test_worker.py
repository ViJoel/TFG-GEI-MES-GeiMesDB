import pytest

from ui.app.worker import Worker
from ui.app.worker_error import WorkerError

# =============================================================================
# run
# =============================================================================


def test_worker_run_success(qtbot):
    """
    Verifica que el Worker ejecuta la función,
    emite la señal de éxito con el resultado y
    siempre emite la señal de finalización.
    """

    worker = Worker(lambda x, y: x + y, 2, 3)

    with qtbot.waitSignal(worker.signals.success) as success_blocker, qtbot.waitSignal(
        worker.signals.finished
    ):

        worker.run()

    assert success_blocker.args == [5]


def test_worker_run_error(qtbot):
    """
    Verifica que si la función lanza una excepción,
    el Worker emite un WorkerError y siempre emite
    la señal de finalización.
    """

    def fail():
        raise RuntimeError("boom")

    worker = Worker(fail)

    with qtbot.waitSignal(worker.signals.error) as error_blocker, qtbot.waitSignal(
        worker.signals.finished
    ):

        worker.run()

    error = error_blocker.args[0]

    assert isinstance(error, WorkerError)
    assert isinstance(error.exception, RuntimeError)
    assert str(error.exception) == "boom"
    assert "RuntimeError: boom" in error.traceback

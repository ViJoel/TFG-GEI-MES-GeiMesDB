import pytest

from ui.app.worker_error import WorkerError


def test_worker_error():
    """
    Verifica que WorkerError almacena correctamente
    la información del error y utiliza slots.
    """

    exception = RuntimeError("boom")
    traceback = "Traceback..."

    error = WorkerError(
        exception=exception,
        traceback=traceback,
    )

    assert error.exception is exception
    assert error.traceback == traceback

    # El dataclass utiliza slots.
    with pytest.raises(AttributeError):
        error.other = "value"

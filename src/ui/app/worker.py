from __future__ import annotations

import traceback

from PySide6.QtCore import (
    QRunnable,
    Slot,
)

from ui.app.worker_error import WorkerError
from ui.app.worker_signals import WorkerSignals


class Worker(QRunnable):
    """
    Ejecuta una función en segundo plano.
    """

    def __init__(self, fn, *args, **kwargs):
        super().__init__()

        self._fn = fn
        self._args = args
        self._kwargs = kwargs

        self.signals = WorkerSignals()

    @Slot()
    def run(self):

        try:

            result = self._fn(
                *self._args,
                **self._kwargs,
            )

            self.signals.result.emit(result)

        except Exception as e:

            self.signals.error.emit(
                WorkerError(
                    exception=e,
                    traceback=traceback.format_exc(),
                )
            )

        finally:

            self.signals.finished.emit()

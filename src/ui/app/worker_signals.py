from __future__ import annotations

from PySide6.QtCore import (
    QObject,
    Signal,
)


class WorkerSignals(QObject):
    """
    Señales emitidas por un Worker.
    """

    result = Signal(object)
    error = Signal(object)
    finished = Signal()

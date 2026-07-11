from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QThreadPool

from ui.app.worker import Worker


class TaskManager:

    def __init__(self):

        self._pool = QThreadPool.globalInstance()

        self._workers: set[Worker] = set()

    def run(
        self,
        fn: Callable,
        *args,
        on_success: Callable | None = None,
        on_error: Callable | None = None,
        on_finished: Callable | None = None,
        **kwargs,
    ) -> None:

        worker = Worker(
            fn,
            *args,
            **kwargs,
        )

        self._workers.add(worker)

        if on_success:
            worker.signals.result.connect(on_success)

        if on_error:
            worker.signals.error.connect(on_error)

        if on_finished:
            worker.signals.finished.connect(on_finished)

        worker.signals.finished.connect(lambda: self._workers.discard(worker))

        self._pool.start(worker)

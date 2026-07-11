from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QThreadPool

from ui.app.worker import Worker


class TaskManager:
    """
    Gestiona la ejecución de tareas en segundo plano.

    Centraliza el uso del ``QThreadPool`` global de Qt
    y proporciona una API sencilla para ejecutar
    operaciones potencialmente costosas sin bloquear
    el hilo principal de la interfaz.

    También mantiene una referencia a los workers
    activos durante su ejecución para evitar que
    sean liberados prematuramente por el recolector
    de basura.
    """

    def __init__(
        self,
    ) -> None:
        """
        Inicializa el gestor de tareas.

        Obtiene la instancia global de ``QThreadPool``
        y prepara el registro interno de workers
        activos.
        """

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
    ) -> Worker:
        """
        Ejecuta una función en segundo plano.

        La función indicada será ejecutada mediante
        un ``Worker`` utilizando el ``QThreadPool``
        global de Qt. Opcionalmente pueden
        registrarse callbacks para recibir el
        resultado, gestionar errores o ser
        notificado cuando la tarea finalice.

        Args:
            fn (Callable):
                Función a ejecutar en segundo plano.

            *args:
                Argumentos posicionales que serán
                pasados a la función.

            on_success (Callable | None):
                Callback invocado cuando la tarea
                finaliza correctamente.

            on_error (Callable | None):
                Callback invocado cuando la tarea
                produce una excepción.

            on_finished (Callable | None):
                Callback invocado al finalizar la
                tarea, independientemente de si
                terminó correctamente o produjo un
                error.

            **kwargs:
                Argumentos nombrados que serán
                pasados a la función.

        Returns:
            Worker:
                Worker creado y enviado al
                ``QThreadPool`` para su ejecución.
                Puede conservarse como referencia
                para consultar su estado o ampliar
                su funcionalidad en el futuro.
        """

        worker = Worker(
            fn,
            *args,
            **kwargs,
        )

        self._workers.add(worker)

        if on_success:
            worker.signals.success.connect(on_success)

        if on_error:
            worker.signals.error.connect(on_error)

        if on_finished:
            worker.signals.finished.connect(on_finished)

        worker.signals.finished.connect(lambda: self._workers.discard(worker))

        self._pool.start(worker)

        return worker

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

    Encapsula una llamada síncrona dentro de un
    ``QRunnable`` para permitir su ejecución
    mediante un ``QThreadPool`` sin bloquear el
    hilo principal de la interfaz.

    El resultado de la ejecución, los posibles
    errores y la finalización de la tarea se
    notifican mediante señales Qt.
    """

    def __init__(
        self,
        fn,
        *args,
        **kwargs,
    ) -> None:
        """
        Inicializa el worker.

        Args:
            fn:
                Función que será ejecutada en
                segundo plano.

            *args:
                Argumentos posicionales que se
                pasarán a la función.

            **kwargs:
                Argumentos nombrados que se
                pasarán a la función.
        """

        super().__init__()

        self._fn = fn
        self._args = args
        self._kwargs = kwargs

        self.signals = WorkerSignals()

    @Slot()
    def run(
        self,
    ) -> None:
        """
        Ejecuta la función asociada al worker.

        Si la ejecución finaliza correctamente,
        se emite la señal de éxito con el
        resultado obtenido.

        Si ocurre una excepción, ésta se
        encapsula en un ``WorkerError`` y se
        emite mediante la señal de error.

        La señal de finalización se emite
        siempre, independientemente del
        resultado de la ejecución.
        """

        try:

            result = self._fn(
                *self._args,
                **self._kwargs,
            )

            self.signals.success.emit(result)

        except Exception as e:

            self.signals.error.emit(
                WorkerError(
                    exception=e,
                    traceback=traceback.format_exc(),
                )
            )

        finally:

            self.signals.finished.emit()

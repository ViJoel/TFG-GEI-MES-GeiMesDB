from dataclasses import dataclass


@dataclass(slots=True)
class WorkerError:
    """
    Información asociada a un error producido
    durante la ejecución de un Worker.
    """

    exception: Exception
    traceback: str

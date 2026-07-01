from enum import Enum


class NotificationType(Enum):
    """
    Tipos de notificación soportados
    por la interfaz gráfica.
    """

    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    INFO = "INFO"
    WARNING = "WARNING"

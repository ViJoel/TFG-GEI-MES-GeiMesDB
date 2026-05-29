"""
Enumeración que define los tipos de notificación
disponibles dentro de la interfaz.

Cada valor representa una categoría visual
y semántica utilizada por el sistema de
notificaciones.

Clases:
    - NotificationType
"""

from enum import Enum


class NotificationType(Enum):
    """
    Tipos de notificación soportados
    por la interfaz gráfica.

    Valores:
        SUCCESS:
            Operación completada correctamente.

        ERROR:
            Error producido durante una operación.

        INFO:
            Mensaje informativo general.
    """

    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    INFO = "INFO"

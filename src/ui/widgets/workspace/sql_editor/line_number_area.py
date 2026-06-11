from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget


class LineNumberArea(QWidget):
    """
    Widget auxiliar encargado de representar
    el área lateral donde se muestran los
    números de línea del editor SQL.

    Responsabilidades:
    - Reservar el espacio necesario para
      los números de línea.
    - Delegar el proceso de pintado en
      el editor asociado.
    """

    def __init__(self, editor):
        """
        Inicializa el área de números
        de línea asociada a un editor.

        Args:
            editor:
                Editor propietario encargado
                del cálculo y pintado del área.
        """

        super().__init__(editor)

        self.editor = editor

    def sizeHint(self) -> QSize:
        """
        Retorna el tamaño recomendado para
        el área de números de línea.

        Returns:
            QSize:
                Tamaño sugerido para el widget.
        """

        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event) -> None:
        """
        Solicita al editor asociado el
        pintado del área de números de línea.

        Args:
            event:
                Evento de pintado recibido
                por Qt.
        """

        self.editor.line_number_area_paint_event(event)

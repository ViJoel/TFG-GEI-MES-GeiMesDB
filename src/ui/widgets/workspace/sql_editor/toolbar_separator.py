from PySide6.QtWidgets import (
    QFrame,
    QSizePolicy,
)


class ToolbarSeparator(QFrame):
    """
    Separador visual utilizado para agrupar botones dentro de la barra
    de herramientas.

    Se implementa como una línea vertical de tamaño fijo para garantizar
    una representación consistente tanto en layouts horizontales como en
    `FlowLayout`.
    """

    def __init__(self):
        """
        Inicializa el separador configurando su apariencia y tamaño fijo.
        """

        super().__init__()

        self.setObjectName("toolbar_separator")

        self.setFrameShape(QFrame.Shape.VLine)
        self.setFrameShadow(QFrame.Shadow.Plain)

        self.setFixedWidth(1)
        self.setFixedHeight(24)

        self.setSizePolicy(
            QSizePolicy.Fixed,
            QSizePolicy.Fixed,
        )

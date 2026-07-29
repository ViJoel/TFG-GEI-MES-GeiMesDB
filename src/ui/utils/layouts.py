from PySide6.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
)

from ui.utils.flow_layout import FlowLayout


def vbox(
    ml: int = 0,
    mt: int = 0,
    mr: int = 0,
    mb: int = 0,
    sp: int = 0,
) -> QVBoxLayout:
    """
    Crea y configura un layout vertical.

    Args:
        ml (int):
            Margen izquierdo.

        mt (int):
            Margen superior.

        mr (int):
            Margen derecho.

        mb (int):
            Margen inferior.

        sp (int):
            Espaciado entre widgets.

    Returns:
        QVBoxLayout:
            Layout vertical configurado.
    """

    layout = QVBoxLayout()

    layout.setContentsMargins(
        ml,
        mt,
        mr,
        mb,
    )

    layout.setSpacing(sp)

    return layout


def hbox(
    ml: int = 0,
    mt: int = 0,
    mr: int = 0,
    mb: int = 0,
    sp: int = 0,
) -> QHBoxLayout:
    """
    Crea y configura un layout horizontal.

    Args:
        ml (int):
            Margen izquierdo.

        mt (int):
            Margen superior.

        mr (int):
            Margen derecho.

        mb (int):
            Margen inferior.

        sp (int):
            Espaciado entre widgets.

    Returns:
        QHBoxLayout:
            Layout horizontal configurado.
    """

    layout = QHBoxLayout()

    layout.setContentsMargins(
        ml,
        mt,
        mr,
        mb,
    )

    layout.setSpacing(sp)

    return layout


def flow(
    ml: int = 0,
    mt: int = 0,
    mr: int = 0,
    mb: int = 0,
    sp: int = 0,
) -> FlowLayout:
    """
    Crea y configura un layout de flujo.

    Los widgets se disponen horizontalmente y, cuando no existe espacio
    suficiente, continúan automáticamente en la siguiente línea.

    Args:
        ml (int):
            Margen izquierdo.

        mt (int):
            Margen superior.

        mr (int):
            Margen derecho.

        mb (int):
            Margen inferior.

        sp (int):
            Espaciado entre widgets.

    Returns:
        FlowLayout:
            Layout de flujo configurado.
    """

    layout = FlowLayout()

    layout.setContentsMargins(
        ml,
        mt,
        mr,
        mb,
    )

    layout.setSpacing(sp)

    return layout

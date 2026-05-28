from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout


def clear_layout(layout):
    """
    Elimina márgenes y spacing de un layout.
    """

    layout.setContentsMargins(0, 0, 0, 0) # Quita el espacio invisible de los bordes del layout
    layout.setSpacing(0) # Quita la separación por defecto entre widgets hijos


def vbox():
    layout = QVBoxLayout()
    clear_layout(layout)
    return layout


def hbox():
    layout = QHBoxLayout()
    clear_layout(layout)
    return layout

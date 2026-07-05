from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout


def vbox(
    ml: int = 0,
    mt: int = 0,
    mr: int = 0,
    mb: int = 0,
    sp: int = 0,
):
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
):
    layout = QHBoxLayout()

    layout.setContentsMargins(
        ml,
        mt,
        mr,
        mb,
    )

    layout.setSpacing(sp)

    return layout

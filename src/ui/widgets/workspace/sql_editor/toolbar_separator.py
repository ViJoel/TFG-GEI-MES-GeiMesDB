from PySide6.QtWidgets import QFrame


class ToolbarSeparator(QFrame):

    def __init__(self):
        super().__init__()

        self.setObjectName("toolbar_separator")

        self.setFrameShape(QFrame.Shape.VLine)
        self.setFrameShadow(QFrame.Shadow.Plain)

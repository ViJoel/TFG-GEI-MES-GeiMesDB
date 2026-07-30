from PySide6.QtWidgets import (
    QProxyStyle,
    QStyle,
)


class NoFocusStyle(QProxyStyle):

    def drawPrimitive(self, element, option, painter, widget=None):
        if element == QStyle.PE_FrameFocusRect:
            return

        super().drawPrimitive(element, option, painter, widget)

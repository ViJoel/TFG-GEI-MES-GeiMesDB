from PySide6.QtCore import (
    QPoint,
    QRect,
    QSize,
    Qt,
)
from PySide6.QtWidgets import (
    QLayout,
    QSizePolicy,
)


class FlowLayout(QLayout):
    """
    Layout que coloca los widgets de izquierda a derecha y
    automáticamente continúa en la siguiente línea cuando
    no hay espacio horizontal suficiente.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self._items = []

    # ==============================
    # === QLayout implementation ===
    # ==============================

    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self._do_layout(
            QRect(0, 0, width, 0),
            test_only=True,
        )

    def setGeometry(self, rect):
        super().setGeometry(rect)

        self._do_layout(
            rect,
            test_only=False,
        )

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()

        for item in self._items:
            size = size.expandedTo(item.minimumSize())

        margins = self.contentsMargins()

        size += QSize(
            margins.left() + margins.right(),
            margins.top() + margins.bottom(),
        )

        return size

    # ===============
    # === PRIVATE ===
    # ===============

    def _do_layout(
        self,
        rect: QRect,
        test_only: bool,
    ) -> int:

        margins = self.contentsMargins()

        x = rect.x() + margins.left()
        y = rect.y() + margins.top()

        line_height = 0

        right = rect.x() + rect.width() - margins.right()

        spacing = self.spacing()

        for item in self._items:

            widget = item.widget()

            style = widget.style() if widget is not None else None

            if style is not None:
                h_spacing = spacing + style.layoutSpacing(
                    QSizePolicy.PushButton,
                    QSizePolicy.PushButton,
                    Qt.Horizontal,
                )
                v_spacing = spacing + style.layoutSpacing(
                    QSizePolicy.PushButton,
                    QSizePolicy.PushButton,
                    Qt.Vertical,
                )
            else:
                h_spacing = spacing
                v_spacing = spacing

            hint = item.sizeHint()

            next_x = x + hint.width()

            if line_height > 0 and next_x > right:
                x = rect.x() + margins.left()
                y += line_height + v_spacing
                next_x = x + hint.width()
                line_height = 0

            if not test_only:
                item.setGeometry(
                    QRect(
                        QPoint(x, y),
                        hint,
                    )
                )

            x = next_x + h_spacing
            line_height = max(
                line_height,
                hint.height(),
            )

        return y + line_height + margins.bottom() - rect.y()

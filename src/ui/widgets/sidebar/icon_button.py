import qtawesome as qta
from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QPushButton

from ui.themes.theme_manager import ThemeManager


class IconButton(QPushButton):

    # ============
    # === INIT ===
    # ============

    def __init__(self, icon_name: str, object_name: str):
        super().__init__()

        self._icon_name = icon_name
        self._object_name = object_name

        self._hover = False
        self._pressed = False

        self.setObjectName(object_name)

        self._icon_cache = {}

        self._apply_icon()

    # ================
    # === UI STATE ===
    # ================

    def _apply_icon(self):

        color_disabled = self._get_color("_disabled")

        if self._pressed:
            color = self._get_color("_pressed")

        elif self._hover:
            color = self._get_color("_hover")

        else:
            color = self._get_color()

        self.setIcon(
            self._make_icon(
                color,
                color_disabled,
            )
        )

    # ==================
    # === UI HELPERS ===
    # ==================

    def _prefix(self):
        return f"button_{self._object_name}_color"

    def _get_color(
        self,
        suffix: str = "",
    ):
        return ThemeManager.get(self._prefix() + suffix)

    def _make_icon(
        self,
        color: str,
        color_disabled: str,
    ):
        key = (self._icon_name, color)

        if key not in self._icon_cache:
            self._icon_cache[key] = qta.icon(
                self._icon_name,
                color=color,
                color_disabled=color_disabled,
            )

        return self._icon_cache[key]

    # ======================
    # === EVENT HANDLERS ===
    # ======================

    def enterEvent(self, e):
        self._hover = True
        self._apply_icon()
        super().enterEvent(e)

    def leaveEvent(self, e):
        self._hover = False
        self._apply_icon()
        super().leaveEvent(e)

    def mousePressEvent(self, e):
        self._pressed = True
        self._apply_icon()
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        self._pressed = False
        self._apply_icon()
        super().mouseReleaseEvent(e)

    def mouseMoveEvent(self, e):
        # seguridad: evita pressed stuck
        if not self.rect().contains(e.pos()):
            self._pressed = False
            self._apply_icon()

        super().mouseMoveEvent(e)

    # ==================
    # === PUBLIC API ===
    # ==================

    def setEnabled(self, enabled: bool):
        super().setEnabled(enabled)
        self._apply_icon()

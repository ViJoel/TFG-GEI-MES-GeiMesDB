import qtawesome as qta
from PySide6.QtCore import (
    QSize,
    Qt,
)
from PySide6.QtWidgets import QToolButton

from ui.themes.theme_manager import ThemeManager


class ToolbarButton(QToolButton):

    # ============
    # === INIT ===
    # ============

    def __init__(
        self,
        icon: str,
        action: str,
        text: str,
    ) -> None:

        super().__init__()

        self.setObjectName("toolbar_button")

        self.setIcon(
            qta.icon(
                icon,
                color=ThemeManager.get_color(f"toolbar_button_{action}_icon_color"),
            )
        )

        self.setIconSize(
            QSize(
                16,
                16,
            )
        )

        self.setText(text)

        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

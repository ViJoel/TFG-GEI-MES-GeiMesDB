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

        self._icon = icon
        self._action = action
        self._text = text

        self._setup_ui()
        self._connect_signals()

    # ================
    # === UI SETUP ===
    # ================

    def _setup_ui(
        self,
    ) -> None:
        """
        Construye la interfaz principal del widget.
        """

        self.setObjectName("toolbar_button")

        self._update_icon()

        self.setIconSize(
            QSize(
                16,
                16,
            )
        )

        self.setText(self._text)

        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

    # ==================
    # === UI HELPERS ===
    # ==================

    def _update_icon(
        self,
    ) -> None:
        """
        Reconstruye el icono utilizando
        los colores del tema activo.
        """

        self.setIcon(
            qta.icon(
                self._icon,
                color=ThemeManager.get_color(
                    f"toolbar_button_{self._action}_icon_color",
                ),
            )
        )

    # ===============
    # === SIGNALS ===
    # ===============

    def _connect_signals(
        self,
    ) -> None:
        """
        Conecta señales de widgets
        con sus handlers correspondientes.
        """

        ThemeManager.events().theme_changed.connect(
            self._on_theme_changed,
        )

    # ======================
    # === EVENT HANDLERS ===
    # ======================

    def _on_theme_changed(
        self,
        _: str,
    ) -> None:
        """
        Actualiza los recursos dependientes
        del tema.
        """

        self._update_icon()

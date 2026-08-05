import qtawesome as qta
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QPushButton

from ui.themes.theme_manager import ThemeManager


class IconButton(QPushButton):

    # ============
    # === INIT ===
    # ============

    def __init__(
        self,
        icon_name: str,
        object_name: str,
    ) -> None:
        """
        Inicializa el botón configurando el icono,
        el nombre del objeto y el estado visual
        inicial.

        Args:
            icon_name (str):
                Nombre del icono compatible con
                QtAwesome.

            object_name (str):
                Nombre del objeto utilizado para
                identificar el botón y resolver
                los colores definidos en el tema.
        """

        super().__init__()

        self._icon_name = icon_name
        self._object_name = object_name

        self._hover = False
        self._pressed = False

        self.setObjectName(object_name)

        self._icon_cache: dict[tuple[str, str, str], QIcon] = {}

        self._connect_signals()

        self._apply_icon()

    # ================
    # === UI STATE ===
    # ================

    def _apply_icon(
        self,
    ) -> None:
        """
        Actualiza el icono mostrado por el botón
        según su estado visual actual.

        El color del icono se selecciona en función
        de si el botón está en estado normal,
        resaltado, pulsado o deshabilitado.
        """

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

    def _prefix(
        self,
    ) -> str:
        """
        Construye el prefijo utilizado para resolver
        las claves de color del tema asociadas al
        botón.

        Returns:
            str:
                Prefijo de las claves de color.
        """

        return f"button_{self._object_name}_color"

    def _get_color(
        self,
        suffix: str = "",
    ) -> str:
        """
        Obtiene un color del tema para el estado
        indicado del botón.

        Args:
            suffix (str):
                Sufijo correspondiente al estado
                visual del botón.

        Returns:
            str:
                Color definido en el tema.
        """

        return ThemeManager.get_color(self._prefix() + suffix)

    def _make_icon(
        self,
        color: str,
        color_disabled: str,
    ) -> QIcon:
        """
        Obtiene un icono coloreado utilizando una
        caché para evitar recreaciones innecesarias.

        Args:
            color (str):
                Color del icono en estado activo.

            color_disabled (str):
                Color utilizado cuando el botón se
                encuentra deshabilitado.

        Returns:
            QIcon:
                Icono configurado con los colores
                indicados.
        """

        key = (
            self._icon_name,
            color,
            color_disabled,
        )

        if key not in self._icon_cache:
            self._icon_cache[key] = qta.icon(
                self._icon_name,
                color=color,
                color_disabled=color_disabled,
            )

        return self._icon_cache[key]

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

        self._icon_cache.clear()
        self._apply_icon()

    # ======================
    # === QT OVERRIDES ===
    # ======================

    def enterEvent(
        self,
        event,
    ) -> None:
        """
        Actualiza el estado de hover al entrar el
        cursor en el botón.
        """

        self._hover = True
        self._apply_icon()
        super().enterEvent(event)

    def leaveEvent(
        self,
        event,
    ) -> None:
        """
        Actualiza el estado de hover al abandonar
        el cursor el botón.
        """

        self._hover = False
        self._apply_icon()
        super().leaveEvent(event)

    def mousePressEvent(
        self,
        event,
    ) -> None:
        """
        Actualiza el estado visual al pulsar el
        botón.
        """

        self._pressed = True
        self._apply_icon()
        super().mousePressEvent(event)

    def mouseReleaseEvent(
        self,
        event,
    ) -> None:
        """
        Restablece el estado visual al liberar el
        botón del ratón.
        """

        self._pressed = False
        self._apply_icon()
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(
        self,
        event,
    ) -> None:
        """
        Corrige el estado de pulsación cuando el
        cursor abandona el botón mientras el ratón
        permanece presionado.
        """

        # Seguridad: Evita pressed stuck.
        if not self.rect().contains(event.pos()):
            self._pressed = False
            self._apply_icon()

        super().mouseMoveEvent(event)

    # ==================
    # === PUBLIC API ===
    # ==================

    def setEnabled(
        self,
        enabled: bool,
    ) -> None:
        """
        Actualiza el estado habilitado del botón y
        refresca su icono.

        Args:
            enabled (bool):
                Indica si el botón debe permanecer
                habilitado.
        """

        super().setEnabled(enabled)
        self._apply_icon()

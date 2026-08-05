from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtGui import QPaintEvent

import qtawesome as qta
from PySide6.QtCore import (
    QSize,
    Qt,
    Signal,
)
from PySide6.QtGui import (
    QFontMetrics,
    QIcon,
    QPainter,
)
from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QSizePolicy,
    QWidget,
)

from entities.file import File
from ui.themes.theme_manager import ThemeManager
from ui.utils.layouts import hbox


class CloseFileButton(QPushButton):
    """
    Botón utilizado para cerrar un archivo desde la lista.

    Permite alternar entre un icono normal y otro que indica
    la existencia de cambios pendientes de guardar.
    """

    # ============
    # === INIT ===
    # ============

    def __init__(
        self,
        parent: QWidget | None = None,
    ) -> None:
        """
        Inicializa el botón configurando su apariencia,
        estado inicial e iconos dependientes del tema.

        Args:
            parent (QWidget | None):
                Widget padre que contendrá este botón.
        """

        super().__init__(parent)

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

        self.setObjectName("files_list_item_close_button")

        self.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground,
            True,
        )

        self.setFixedSize(16, 16)

        # Asegura que el layout no deforme el botón.
        self.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Fixed,
        )

        self._create_icons()

        # Estado inicial.
        self._alternative_state = False
        self.setIcon(
            self._current_icon(),
        )

        self.setToolTip(
            self.tr(
                "Close the editor tab.<br><br><b>Shortcut:</b> <code>Ctrl + W</code>"
            )
        )

    # ==================
    # === UI HELPERS ===
    # ==================

    def _create_icons(
        self,
    ) -> None:
        """
        Genera y almacena en caché los objetos QIcon de QtAwesome.

        Lee el esquema de color actual a través de ThemeManager y
        precompila las fuentes de Material Design Icons para evitar
        renderizados repetitivos durante la ejecución de eventos.
        """

        color = ThemeManager.get_color(
            "files_list_item_color",
        )

        self._icon_default = qta.icon(
            "mdi.close",
            color=color,
        )

        self._icon_alt = qta.icon(
            "mdi.close-circle",
            color=color,
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
        Actualiza los recursos dependientes del tema.
        """

        self._create_icons()

        self.setIcon(
            self._current_icon(),
        )

    # ===================
    # === PRIVATE API ===
    # ===================

    def _current_icon(
        self,
    ) -> QIcon:
        """
        Devuelve el icono que corresponde al estado
        visual actual del botón.

        Returns:
            QIcon:
                Icono por defecto o alternativo según
                el estado almacenado.
        """

        return self._icon_alt if self._alternative_state else self._icon_default

    # ==================
    # === PUBLIC API ===
    # ==================

    def set_alternative_state(
        self,
        use_alternative: bool,
    ) -> None:
        """
        Actualiza el estado visual del botón.

        Si el cursor no se encuentra sobre el botón,
        el icono correspondiente se aplica de forma
        inmediata. En caso contrario, el cambio se
        reflejará al finalizar el estado de hover.

        Args:
            use_alternative (bool):
                - `True` para utilizar el icono alternativo.
                - `False` para utilizar el icono por defecto.
        """

        self._alternative_state = use_alternative

        # Si el ratón no está encima, aplicamos el cambio visual inmediatamente
        if not self.underMouse():
            self.setIcon(
                self._current_icon(),
            )


class ElidedLabel(QLabel):
    """
    Etiqueta que muestra el texto truncado con puntos suspensivos
    cuando el espacio horizontal disponible no es suficiente.
    """

    # ============
    # === INIT ===
    # ============

    def __init__(
        self,
        text: str = "",
        parent: QWidget | None = None,
    ) -> None:
        """
        Inicializa la etiqueta almacenando el texto completo
        para poder recalcular su representación elidida cuando
        cambie el tamaño del widget.

        Args:
            text (str):
                Texto de la etiqueta.

            parent (QWidget | None):
                Widget padre.
        """

        super().__init__(
            text,
            parent,
        )

        self.setObjectName("files_list_item_label")

        self.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground,
            True,
        )

        # Guardamos el texto completo original para recalcularlo
        # siempre bien.
        self._full_text = text

        # Le decimos al layout que este widget puede expandirse
        # o encogerse libremente.
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )

    # ====================
    # === QT OVERRIDES ===
    # ====================

    def minimumSizeHint(
        self,
    ) -> QSize:
        """
        Reduce el ancho mínimo recomendado para permitir que
        el layout comprima la etiqueta cuando sea necesario.

        Returns:
            QSize:
                Tamaño mínimo recomendado.
        """

        # Reemplazamos el tamaño mínimo
        # recomendado por uno muy bajo.
        return QSize(
            0,
            super().minimumSizeHint().height(),
        )

    def paintEvent(
        self,
        event: QPaintEvent,
    ) -> None:
        """
        Dibuja el texto aplicando elisión cuando no cabe
        completamente en el ancho disponible.

        Args:
            event (QPaintEvent):
                Evento de pintado recibido desde Qt.
        """

        # Creamos el pintor para dibujar el texto manualmente.
        painter = QPainter(self)
        metrics = QFontMetrics(self.font())

        # Calculamos el texto con "..." (elisión) según el
        # ancho actual del QLabel.
        elided_text = metrics.elidedText(
            self._full_text,
            Qt.TextElideMode.ElideRight,  # Coloca los ... a la derecha.
            self.width(),
        )

        # Dibujamos el texto alineado correctamente.
        painter.drawText(
            self.rect(),
            self.alignment(),
            elided_text,
        )

    # ==================
    # === PUBLIC API ===
    # ==================

    def setText(
        self,
        text: str,
    ) -> None:
        """
        Actualiza el texto completo de la etiqueta y solicita
        su repintado.

        Args:
            text(str):
                Nuevo texto que debe mostrarse.
        """

        self._full_text = text
        super().setText(text)
        self.update()


class FilesListItem(QWidget):
    """
    Representación visual de un archivo dentro de la lista
    de archivos abiertos.
    """

    # =================
    # === VARIABLES ===
    # =================

    close_requested = Signal(QWidget)

    # ============
    # === INIT ===
    # ============

    def __init__(
        self,
        file: File,
    ) -> None:
        """
        Inicializa el elemento asociándolo al archivo indicado.

        Args:
            file (File):
                Archivo representado por el elemento.
        """

        super().__init__()

        self.file = file

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

        self.setObjectName("files_list_item")

        self.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground,
            True,
        )

        layout = hbox(
            ml=8,
            mt=4,
            mr=8,
            mb=4,
            sp=4,
        )
        self.setLayout(layout)

        self.file_name_label = ElidedLabel()
        self.file_name_label.setText(self.file.name)
        # Desactivar toda interacción con el texto.
        self.file_name_label.setTextInteractionFlags(Qt.NoTextInteraction)

        self.close_button = CloseFileButton(parent=self)

        layout.addWidget(self.file_name_label)
        layout.addWidget(self.close_button)

        layout.setSizeConstraint(layout.SizeConstraint.SetNoConstraint)
        layout.setStretch(0, 1)  # label
        layout.setStretch(1, 0)  # botón

    # ================
    # === UI STATE ===
    # ================

    def set_selected(
        self,
        selected: bool,
    ) -> None:
        """
        Actualiza el estado de selección del item.

        Args:
            selected (bool): Estado de selección.
        """

        self.setProperty(
            "selected",
            "true" if selected else "false",
        )

        self._refresh_style()

    def _refresh_style(
        self,
    ) -> None:
        """
        Reaplica el estilo del widget.
        """

        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

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

        self.close_button.clicked.connect(self._on_close_clicked)

    # ======================
    # === EVENT HANDLERS ===
    # ======================

    def _on_close_clicked(
        self,
    ) -> None:
        """
        Notifica que el usuario ha solicitado cerrar
        el archivo representado por este elemento.
        """

        self.close_requested.emit(self)

    # ==================
    # === PUBLIC API ===
    # ==================

    def refresh(
        self,
    ) -> None:
        """
        Actualiza la representación visual del archivo.
        """

        self.file_name_label.setText(
            self.file.name,
        )

        self.close_button.set_alternative_state(self.file.has_changes)

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QLabel,
    QPushButton,
    QSizePolicy,
    QWidget,
)

from entities.message_type import MessageType
from log.app_logger import get_logger
from ui.app.app_actions import notify
from ui.app.app_context import AppContext
from ui.themes.theme_manager import ThemeManager
from ui.utils.layouts import (
    hbox,
    vbox,
)

logger = get_logger(__name__)


class SettingsMenu(QWidget):

    # =================
    # === VARIABLES ===
    # =================

    # ============
    # === INIT ===
    # ============

    def __init__(
        self,
    ) -> None:

        super().__init__()

        self.themes = ThemeManager.get_themes()

        self._setup_ui()
        self._connect_signals()

        # Estado inicial.
        self._on_setting_changed()

    # ================
    # === UI SETUP ===
    # ================

    def _setup_ui(
        self,
    ) -> None:
        """
        Construye la interfaz principal del widget.
        """

        self.setObjectName("settings_menu")

        self.setFixedWidth(480)

        self.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground,
            True,
        )

        layout = vbox(
            ml=32,
            mt=24,
            mr=32,
            mb=24,
            sp=16,
        )
        self.setLayout(layout)

        self._build_form_title(layout)

        layout.addLayout(self._create_theme_setting())
        layout.addStretch()
        layout.addLayout(self._create_buttons())

        self.setFixedHeight(self.sizeHint().height())

    # ================
    # === UI STATE ===
    # ================

    # ==================
    # === UI HELPERS ===
    # ==================

    def _build_form_title(
        self,
        parent_layout,
    ) -> None:
        """
        Construye el título principal
        del formulario.
        """

        title_label = QLabel()

        title_label.setObjectName("settings_menu_title")

        title_label.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Maximum,
        )

        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label.setText(
            self.tr("Settings menu"),
        )

        parent_layout.addWidget(title_label)

    def _create_theme_setting(
        self,
    ):
        """
        Crea el ajuste de selección del tema.
        """

        layout = vbox(sp=8)

        self.theme_label = QLabel(
            self.tr("Theme"),
        )
        self.theme_label.setObjectName("settings_menu_input_label")

        self.theme_input = QComboBox()
        self.theme_input.setObjectName("settings_menu_input")

        # Cargar temas disponibles
        self.theme_input.addItems(self.themes["themes"])

        # Seleccionar el tema actual
        index = self.theme_input.findText(self.themes["current_theme"])

        if index >= 0:
            self.theme_input.setCurrentIndex(index)

        layout.addWidget(self.theme_label)
        layout.addWidget(self.theme_input)

        return layout

    def _create_buttons(
        self,
    ):
        """
        Crea los botones de acción del menú.
        """

        layout = hbox(sp=8)

        self.cancel_button = QPushButton(
            self.tr("Cancel"),
        )
        self.cancel_button.setObjectName("settings_menu_cancel_button")
        self.cancel_button.setProperty("type", "danger")

        self.apply_button = QPushButton(
            self.tr("Apply"),
        )
        self.apply_button.setObjectName("settings_menu_apply_button")
        self.apply_button.setProperty("type", "secondary")

        self.accept_button = QPushButton(
            self.tr("Accept"),
        )
        self.accept_button.setObjectName("settings_menu_accept_button")
        self.accept_button.setProperty("type", "primary")

        layout.addStretch()
        layout.addWidget(self.cancel_button)
        layout.addWidget(self.apply_button)
        layout.addWidget(self.accept_button)

        return layout

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

        # Inputs.
        self.theme_input.currentTextChanged.connect(
            self._on_setting_changed,
        )

        # Botones.
        self.apply_button.clicked.connect(
            self._on_apply_requested,
        )

        self.accept_button.clicked.connect(
            self._on_apply_requested,
        )

    # ======================
    # === EVENT HANDLERS ===
    # ======================

    def _on_setting_changed(
        self,
    ) -> None:

        dirty = self._has_pending_changes()

        self.apply_button.setEnabled(dirty)
        self.accept_button.setEnabled(dirty)

    def _on_apply_requested(
        self,
    ) -> None:

        try:

            logger.info("Changing theme...")

            notify(
                message_type=MessageType.WARNING,
                message=self.tr("Changing theme..."),
            )

            # Fuerza el repintado de la interfaz para que la
            # notificación sea visible antes de iniciar una
            # operación síncrona potencialmente bloqueante.
            AppContext.get_app().processEvents()

            self._apply_theme()

            # Al aplicar ya no quedan cambios pendientes
            self._on_setting_changed()

            logger.success("Theme changed.")

            notify(
                message_type=MessageType.SUCCESS,
                message=self.tr("Theme changed."),
            )
        except Exception as e:
            logger.error(f"Error changin theme: {e}")

            notify(
                message_type=MessageType.SUCCESS,
                message=self.tr("Error changing theme.\nSee logs for details."),
            )

            return

    # =====================
    # === EVENT HELPERS ===
    # =====================

    def _has_pending_changes(
        self,
    ) -> bool:

        return self.theme_input.currentText() != ThemeManager.current_theme()

    def _apply_theme(
        self,
    ) -> None:

        ThemeManager.set_theme(
            self.theme_input.currentText(),
        )

    # ====================
    # === QT OVERRIDES ===
    # ====================

    # ===================
    # === PRIVATE API ===
    # ===================

    # ==================
    # === PUBLIC API ===
    # ==================

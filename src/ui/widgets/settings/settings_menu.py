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
from ui.translations.translation_manager import TranslationManager
from ui.utils.layouts import (
    hbox,
    vbox,
)
import traceback

logger = get_logger(__name__)


class SettingsMenu(QWidget):

    # ============
    # === INIT ===
    # ============

    def __init__(
        self,
    ) -> None:

        super().__init__()

        self.themes = ThemeManager.get_themes()
        self.languages = TranslationManager.get_languages()

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
        layout.addLayout(self._create_language_setting())
        layout.addStretch()
        layout.addLayout(self._create_buttons())

        self.setFixedHeight(self.sizeHint().height())

        self._retranslate_ui()

    def _retranslate_ui(
        self,
    ) -> None:

        self.title_label.setText(
            self.tr("Settings menu"),
        )

        self.theme_label.setText(
            self.tr("Theme"),
        )

        self.language_label.setText(
            self.tr("Language"),
        )

        self.cancel_button.setText(
            self.tr("Cancel"),
        )

        self.apply_button.setText(
            self.tr("Apply"),
        )

        self.accept_button.setText(
            self.tr("Accept"),
        )

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

        self.title_label = QLabel()

        self.title_label.setObjectName("settings_menu_title")

        self.title_label.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Maximum,
        )

        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        parent_layout.addWidget(self.title_label)

    def _create_theme_setting(
        self,
    ):
        """
        Crea el ajuste de selección del tema.
        """

        layout = vbox(sp=8)

        self.theme_label = QLabel()
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

    def _create_language_setting(
        self,
    ):
        """
        Crea el ajuste de selección del idioma.
        """

        layout = vbox(sp=8)

        self.language_label = QLabel()
        self.language_label.setObjectName("settings_menu_input_label")

        self.language_input = QComboBox()
        self.language_input.setObjectName("settings_menu_input")

        for code, name in self.languages["languages"].items():
            self.language_input.addItem(name, code)

        index = self.language_input.findData(
            self.languages["current_language"],
        )

        if index >= 0:
            self.language_input.setCurrentIndex(index)

        layout.addWidget(self.language_label)
        layout.addWidget(self.language_input)

        return layout

    def _create_buttons(
        self,
    ):
        """
        Crea los botones de acción del menú.
        """

        layout = hbox(sp=8)

        self.cancel_button = QPushButton()
        self.cancel_button.setObjectName("settings_menu_cancel_button")
        self.cancel_button.setProperty("type", "danger")

        self.apply_button = QPushButton()
        self.apply_button.setObjectName("settings_menu_apply_button")
        self.apply_button.setProperty("type", "secondary")

        self.accept_button = QPushButton()
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

        self.language_input.currentIndexChanged.connect(
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

            logger.info("Changing settings...")

            notify(
                message_type=MessageType.WARNING,
                message=self.tr("Changing settings..."),
            )

            # Fuerza el repintado de la interfaz para que la
            # notificación sea visible antes de iniciar una
            # operación síncrona potencialmente bloqueante.
            AppContext.get_app().processEvents()

            self._apply_settings()

            self._retranslate_ui()

            # Al aplicar ya no quedan cambios pendientes
            self._on_setting_changed()

            logger.success("Settings changed.")

            notify(
                message_type=MessageType.SUCCESS,
                message=self.tr("Settings changed."),
            )
        except Exception as e:
            logger.error(f"Error changing settings: {e}\n")
            traceback.print_exc()

            notify(
                message_type=MessageType.ERROR,
                message=self.tr("Error changing settings.")
                + "\n"
                + self.tr("See logs for details."),
            )

            return

    # =====================
    # === EVENT HELPERS ===
    # =====================

    def _has_pending_changes(
        self,
    ) -> bool:

        theme_changed = self.theme_input.currentText() != ThemeManager.current_theme()

        language_changed = (
            self.language_input.currentData() != TranslationManager.current_language()
        )

        return theme_changed or language_changed

    def _apply_settings(
        self,
    ) -> None:

        ThemeManager.set_theme(
            self.theme_input.currentText(),
        )

        TranslationManager.set_language(
            self.language_input.currentData(),
        )

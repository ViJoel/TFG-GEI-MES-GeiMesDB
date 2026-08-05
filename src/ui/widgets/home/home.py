from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QSizePolicy,
    QWidget,
)

from common.constants import APP_NAME
from ui.translations.translation_manager import TranslationManager
from ui.utils.layouts import vbox
from ui.widgets.logos.app_logo import AppLogo


class Home(QWidget):
    """
    Pantalla de inicio de la aplicación.

    Responsabilidades:
    - Mostrar la identidad visual de la aplicación.
    - Actuar como pantalla de bienvenida.
    """

    # ============
    # === INIT ===
    # ============

    def __init__(
        self,
    ) -> None:
        """
        Inicializa la pantalla HOME.
        """

        super().__init__()

        self.setObjectName("home_page")

        self._setup_ui()
        self._connect_signals()

    # ================
    # === UI SETUP ===
    # ================

    def _setup_ui(
        self,
    ) -> None:
        """
        Construye la interfaz principal
        de la pantalla.
        """

        # Layout principal vertical.
        main_layout = vbox()

        self.setLayout(main_layout)

        self.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground,
            True,
        )

        # Permitir expansión completa.
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        # Espacio superior.
        main_layout.addStretch()

        # Logo principal.
        logo = AppLogo(size=300)

        main_layout.addWidget(
            logo,
            alignment=Qt.AlignmentFlag.AlignCenter,
        )

        main_layout.addSpacing(40)

        # Texto principal.
        title_label = QLabel(APP_NAME)
        title_label.setObjectName("home_page_title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(
            title_label,
            alignment=Qt.AlignmentFlag.AlignCenter,
        )

        # Texto principal.
        self.slogan_label = QLabel()
        self.slogan_label.setObjectName("home_page_slogan")
        self.slogan_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(
            self.slogan_label,
            alignment=Qt.AlignmentFlag.AlignCenter,
        )

        # Espacio inferior.
        main_layout.addStretch()

        self._retranslate_ui()

    def _retranslate_ui(
        self,
    ) -> None:
        """
        Actualiza todos los textos traducibles del widget.

        Los textos se generan en el momento de la llamada
        utilizando el traductor activo de Qt, permitiendo
        refrescar la interfaz después de cambiar el idioma
        de la aplicación.
        """

        self.slogan_label.setText(
            self.tr("Everything you need. Nothing you don't."),
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

        TranslationManager.events().language_changed.connect(
            self._retranslate_ui,
        )

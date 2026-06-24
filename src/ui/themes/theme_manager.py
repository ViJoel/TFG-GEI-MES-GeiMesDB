import logging
from string import Template

from ui.common.paths import STYLE_FILES
from ui.themes import dark

logger = logging.getLogger(__name__)


# TODO: Actualizar para que use la instancia de la aplicación desde el estado global.
class ThemeManager:
    """
    Gestor central de temas de la aplicación.

    Responsible de cargar, aplicar y resolver valores
    de la paleta de colores activa, así como de inyectarlos
    en los archivos QSS mediante sustitución de variables.

    El sistema permite definir múltiples temas (dark, light, etc.)
    y cambiar dinámicamente entre ellos en tiempo de ejecución.
    """

    _themes = {
        "dark": dark.THEME,
    }

    _current_theme = "dark"

    # ======================
    # === INITIALIZATION ===
    # ======================

    @classmethod
    def initialize(cls, app):
        """
        Inicializa el ThemeManager aplicando el tema activo
        al QApplication.

        Args:
            app (QApplication):
                Instancia de la aplicación Qt.
        """

        logger.info("Initializing theme manager...")

        cls.apply(app)

        logger.success("Theme manager initialized.")

    # ===================
    # === APPLY THEME ===
    # ===================

    @classmethod
    def apply(cls, app):
        """
        Aplica el tema actual generando y estableciendo
        la hoja de estilos global (QSS).

        Args:
            app (QApplication):
                Instancia de la aplicación Qt.
        """

        logger.info(
            "Applying theme '%s'...",
            cls._current_theme,
        )

        app.setStyleSheet(cls._build_stylesheet())

        logger.success(
            "Theme '%s' applied successfully.",
            cls._current_theme,
        )

    # =======================
    # === THEME SWITCHING ===
    # =======================

    @classmethod
    def set_theme(cls, app, theme_name):
        """
        Cambia el tema activo de la aplicación.

        Args:
            app (QApplication):
                Instancia de la aplicación Qt.

            theme_name (str):
                Nombre del tema a activar.

        Raises:
            ValueError:
                Si el tema no está registrado.
        """

        if theme_name not in cls._themes:

            logger.error(
                "Theme '%s' is not registered.",
                theme_name,
            )

            raise ValueError(f"Theme '{theme_name}' is not registered.")

        logger.info(
            "Switching theme from '%s' to '%s'.",
            cls._current_theme,
            theme_name,
        )

        cls._current_theme = theme_name

        cls.apply(app)

    # ==================
    # === THEME INFO ===
    # ==================

    @classmethod
    def current_theme(cls):
        """
        Retorna el nombre del tema actualmente activo.

        Returns:
            str:
                Nombre del tema activo.
        """

        return cls._current_theme

    # ===========================
    # === INTERNAL STYLESHEET ===
    # ===========================

    @classmethod
    def _build_stylesheet(cls):
        """
        Construye la hoja de estilos global (QSS)
        reemplazando variables definidas en el tema
        dentro de los archivos de estilo.

        Returns:
            str:
                QSS final con variables resueltas.
        """

        logger.debug(
            "Building stylesheet for theme '%s'.",
            cls._current_theme,
        )

        stylesheet = ""

        for file in STYLE_FILES:

            logger.debug(
                "Loading stylesheet file: %s",
                file,
            )

            with open(file, encoding="utf-8") as f:

                stylesheet += f.read()

        try:

            stylesheet = Template(stylesheet).substitute(
                cls._themes[cls._current_theme]
            )

        except KeyError as e:

            logger.error(
                "Missing theme variable in QSS: %s",
                e,
            )

            raise

        logger.debug("Stylesheet built successfully.")

        return stylesheet

    # ====================
    # === COLOR ACCESS ===
    # ====================

    @classmethod
    def get_color(
        cls,
        key: str,
    ):
        """
        Obtiene un color o valor de la paleta del tema actual.

        Args:
            key (str):
                Clave del color en la paleta.

        Returns:
            str:
                Valor asociado a la clave.
                Si la clave no existe, devuelve el fallback
                definido por el tema actual.
        """

        colors = cls._themes[cls._current_theme]

        if key in colors:
            return colors[key]

        fallback_color = colors.get("fallback_color", "transparent")

        logger.warning(
            "Theme color '%s' not found in theme '%s'. Using fallback color '%s'.",
            key,
            cls._current_theme,
            fallback_color,
        )

        return fallback_color

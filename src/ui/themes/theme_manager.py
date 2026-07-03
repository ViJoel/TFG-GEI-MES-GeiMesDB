from string import Template

from log.app_logger import get_logger
from ui.app.app_context import AppContext
from ui.common.paths import STYLE_FILES
from ui.themes import dark

logger = get_logger(__name__)

type ThemePalette = dict[str, str]


class ThemeManager:
    """
    Gestor central de temas de la aplicación.

    Responsable de gestionar los temas disponibles,
    aplicar el tema activo a la aplicación y resolver
    las variables utilizadas en los archivos QSS.

    Permite cambiar dinámicamente el tema en tiempo
    de ejecución y consultar los valores de la paleta
    activa.
    """

    _themes: dict[str, ThemePalette] = {
        "dark": dark.THEME,
    }

    _current_theme: str = "dark"

    # ======================
    # === INITIALIZATION ===
    # ======================

    @classmethod
    def initialize(
        cls,
    ) -> None:
        """
        Inicializa el gestor de temas aplicando
        el tema activo a la aplicación.

        Raises:
            RuntimeError:
                Si AppContext no ha sido inicializado.
        """

        logger.info("Initializing theme manager...")

        cls.apply()

        logger.success("Theme manager initialized.")

    # ===================
    # === APPLY THEME ===
    # ===================

    @classmethod
    def apply(
        cls,
    ) -> None:
        """
        Aplica el tema activo a la aplicación.

        Genera la hoja de estilos (QSS) correspondiente
        al tema actual y la establece como hoja de estilos
        global de la aplicación.

        Raises:
            RuntimeError:
                Si AppContext no ha sido inicializado.
        """

        app = AppContext.get_app()

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
    def set_theme(
        cls,
        theme_name: str,
    ) -> None:
        """
        Cambia el tema activo de la aplicación.

        Args:
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

        cls.apply()

    # ==================
    # === THEME INFO ===
    # ==================

    @classmethod
    def current_theme(
        cls,
    ) -> str:
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
    def _build_stylesheet(
        cls,
    ) -> str:
        """
        Construye la hoja de estilos global (QSS)
        reemplazando las variables definidas en el
        tema activo dentro de los archivos QSS.

        Returns:
            str:
                Hoja de estilos QSS con todas las
                variables del tema resueltas.

        Raises:
            KeyError:
                Si alguna variable utilizada en un
                archivo QSS no existe en la paleta
                del tema activo.
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
    ) -> str:
        """
        Obtiene un color o valor de la paleta del tema actual.

        Args:
            key (str):
                Clave del color en la paleta.

        Returns:
            str:
                Valor asociado a la clave. Si la clave
                no existe, devuelve el color de reserva
                definido por el tema activo o
                `"transparent"` si no está definido.
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

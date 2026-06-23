from string import Template

from ui.common.paths import STYLE_FILES
from ui.themes import dark


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
        "dark": dark.COLORS,
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

        cls.apply(app)

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

        app.setStyleSheet(cls._build_stylesheet())

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
            raise ValueError(f"Theme '{theme_name}' is not registered.")

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

        stylesheet = ""

        for file in STYLE_FILES:

            with open(file, encoding="utf-8") as f:

                stylesheet += f.read()

        return Template(stylesheet).substitute(cls._themes[cls._current_theme])

    # ====================
    # === COLOR ACCESS ===
    # ====================

    @classmethod
    def get(
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
                Valor asociado a la clave (normalmente un hex color).
        """

        return cls._themes[cls._current_theme][key]

from string import Template

from ui.common.paths import STYLE_FILES
from ui.themes import dark


class ThemeManager:

    _themes = {
        "dark": dark.COLORS,
    }

    _current_theme = "dark"

    @classmethod
    def initialize(cls, app):

        cls.apply(app)

    @classmethod
    def apply(cls, app):

        app.setStyleSheet(cls._build_stylesheet())

    @classmethod
    def set_theme(cls, app, theme_name):

        if theme_name not in cls._themes:
            raise ValueError(f"Theme '{theme_name}' is not registered.")

        cls._current_theme = theme_name

        cls.apply(app)

    @classmethod
    def current_theme(cls):

        return cls._current_theme

    @classmethod
    def _build_stylesheet(cls):

        stylesheet = ""

        for file in STYLE_FILES:

            with open(file, encoding="utf-8") as f:

                stylesheet += f.read()

        return Template(stylesheet).substitute(cls._themes[cls._current_theme])

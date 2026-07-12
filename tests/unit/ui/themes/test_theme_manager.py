from unittest.mock import (
    MagicMock,
    mock_open,
    patch,
)

import pytest

from ui.themes.theme_manager import ThemeManager

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture(autouse=True)
def restore_theme():
    """
    Restaura el estado del ThemeManager entre tests.
    """
    original = ThemeManager._current_theme
    yield
    ThemeManager._current_theme = original


# =============================================================================
# INITIALIZATION
# =============================================================================


@patch("ui.themes.theme_manager.AppContext.get_app")
@patch.object(ThemeManager, "apply")
def test_initialize(mock_apply, mock_get_app):
    """
    Debe inicializar el gestor aplicando el tema.
    """

    mock_get_app.return_value = MagicMock()

    ThemeManager.initialize()

    mock_apply.assert_called_once()


# =============================================================================
# APPLY
# =============================================================================


@patch("ui.themes.theme_manager.AppContext.get_app")
@patch.object(ThemeManager, "_build_stylesheet")
def test_apply(mock_build, mock_get_app):
    """
    Debe aplicar el stylesheet a la aplicación.
    """

    app = MagicMock()

    mock_get_app.return_value = app
    mock_build.return_value = "QWidget{}"

    ThemeManager.apply()

    app.setStyleSheet.assert_called_once_with("QWidget{}")


# =============================================================================
# THEME SWITCHING
# =============================================================================


@patch.object(ThemeManager, "apply")
def test_set_theme_changes_current_theme(mock_apply):
    """
    Debe cambiar el tema activo.
    """

    ThemeManager.set_theme("dark")

    assert ThemeManager.current_theme() == "dark"
    mock_apply.assert_called_once()


def test_set_theme_invalid():
    """
    Debe lanzar ValueError para temas inexistentes.
    """

    with pytest.raises(ValueError):
        ThemeManager.set_theme("invalid-theme")


# =============================================================================
# CURRENT THEME
# =============================================================================


def test_current_theme():
    """
    Debe devolver el tema activo.
    """

    ThemeManager._current_theme = "dark"

    assert ThemeManager.current_theme() == "dark"


# =============================================================================
# BUILD STYLESHEET
# =============================================================================


@patch("builtins.open", new_callable=mock_open, read_data="QWidget{color:$text;}")
@patch("ui.themes.theme_manager.STYLE_FILES", ["style.qss"])
def test_build_stylesheet(mock_file):
    """
    Debe construir correctamente el stylesheet.
    """

    ThemeManager._themes["dark"] = {"text": "#fff"}

    stylesheet = ThemeManager._build_stylesheet()

    assert stylesheet == "QWidget{color:#fff;}"


@patch("builtins.open", new_callable=mock_open, read_data="QWidget{color:$missing;}")
@patch("ui.themes.theme_manager.STYLE_FILES", ["style.qss"])
def test_build_stylesheet_missing_variable(mock_file):
    """
    Debe propagar KeyError si falta una variable.
    """

    ThemeManager._themes["dark"] = {}

    with pytest.raises(KeyError):
        ThemeManager._build_stylesheet()


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data="QWidget { color: @primary; }",
)
@patch("ui.themes.theme_manager.STYLE_FILES", ["style.qss"])
def test_build_stylesheet_invalid_at_variable(mock_file):
    """
    Debe lanzar ValueError si un QSS utiliza
    variables con '@' en lugar de '$'.
    """

    ThemeManager._themes["dark"] = {
        "primary": "#ffffff",
    }

    with pytest.raises(
        ValueError,
        match=r"Theme variables must use '\$', not '@'\.",
    ):
        ThemeManager._build_stylesheet()


# =============================================================================
# GET COLOR
# =============================================================================


def test_get_color_existing():
    """
    Debe devolver un color existente.
    """

    ThemeManager._themes["dark"] = {
        "primary": "#111",
        "fallback_color": "#222",
    }

    assert ThemeManager.get_color("primary") == "#111"


def test_get_color_fallback():
    """
    Debe devolver el color de reserva.
    """

    ThemeManager._themes["dark"] = {
        "fallback_color": "#999",
    }

    assert ThemeManager.get_color("unknown") == "#999"


def test_get_color_default_transparent():
    """
    Debe devolver transparent si no existe fallback_color.
    """

    ThemeManager._themes["dark"] = {}

    assert ThemeManager.get_color("unknown") == "transparent"

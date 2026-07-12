from unittest.mock import (
    MagicMock,
    patch,
)

import pytest

from entities.message_type import MessageType
from entities.script_result import ScriptResult
from ui.widgets.workspace.results_view.console import Console

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def console(qtbot):
    """
    Crea una instancia de Console registrada en qtbot.
    """

    widget = Console()
    qtbot.addWidget(widget)

    return widget


@pytest.fixture
def script_result():
    """
    Crea un ScriptResult simulado con items.
    """

    item1 = MagicMock()
    item1.query = "SELECT 1;"
    item1.success = True
    item1.error = None

    item2 = MagicMock()
    item2.query = "SELECT 2;"
    item2.success = False
    item2.error = "Syntax error"

    result = MagicMock(spec=ScriptResult)
    result.items = [item1, item2]

    return result


@pytest.fixture(autouse=True)
def patch_theme_manager():
    """
    Evita dependencia del ThemeManager real.
    """

    with patch(
        "ui.widgets.workspace.results_view.console.ThemeManager.get_color",
        return_value="#FFFFFF",
    ):
        yield


# =============================================================================
# CLEAR OUTPUT
# =============================================================================


def test_clear_output_clears_console(console):
    """
    Verifica que clear_output elimina el contenido
    de la consola.
    """

    console.setText("Some text")

    console.clear_output()

    assert console.toPlainText() == ""


# =============================================================================
# WRITE
# =============================================================================


def test_write_default_message(console):
    """
    Verifica que write usa el color DEFAULT.
    """

    console._append_colored_text = MagicMock()

    console.write("Hello")

    console._append_colored_text.assert_called_once()

    args = console._append_colored_text.call_args.kwargs

    assert args["text"] == "Hello"
    assert args["color"] is not None


def test_write_info_message(console):
    """
    Verifica que write usa el color INFO.
    """

    console._append_colored_text = MagicMock()

    console.write("Info message", MessageType.INFO)

    args = console._append_colored_text.call_args.kwargs

    assert args["text"] == "Info message"
    assert args["color"] is not None


def test_write_success_message(console):
    """
    Verifica que write usa el color SUCCESS.
    """

    console._append_colored_text = MagicMock()

    console.write("OK", MessageType.SUCCESS)

    args = console._append_colored_text.call_args.kwargs

    assert args["text"] == "OK"
    assert args["color"] is not None


def test_write_warning_message(console):
    """
    Verifica que write usa el color WARNING.
    """

    console._append_colored_text = MagicMock()

    console.write("Warning!", MessageType.WARNING)

    args = console._append_colored_text.call_args.kwargs

    assert args["text"] == "Warning!"
    assert args["color"] is not None


def test_write_error_message(console):
    """
    Verifica que write usa el color ERROR.
    """

    console._append_colored_text = MagicMock()

    console.write("Error!", MessageType.ERROR)

    args = console._append_colored_text.call_args.kwargs

    assert args["text"] == "Error!"
    assert args["color"] is not None


# =============================================================================
# SHOW SCRIPT RESULT
# =============================================================================


def test_show_script_result_success_and_error(console, script_result):
    """
    Verifica que show_script_result escribe
    correctamente resultados exitosos y errores.
    """

    console.write = MagicMock()
    console.clear = MagicMock()

    console.show_script_result(script_result)

    console.clear.assert_called_once()

    assert console.write.call_count == 2

    console.write.assert_any_call(
        "SELECT 1;\n\n",
        MessageType.SUCCESS,
    )

    console.write.assert_any_call(
        "SELECT 2;\nError: Syntax error\n\n",
        MessageType.ERROR,
    )


def test_show_script_result_none(console):
    """
    Verifica que si script_result es None
    no se escribe nada.
    """

    console.write = MagicMock()
    console.clear = MagicMock()

    console.show_script_result(None)

    console.clear.assert_called_once()
    console.write.assert_not_called()

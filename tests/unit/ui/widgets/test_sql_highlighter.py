import re
from unittest.mock import MagicMock

import pytest
from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import (
    QFont,
    QSyntaxHighlighter,
    QTextCharFormat,
    QTextDocument,
)

from ui.widgets.workspace.sql_editor.sql_highlighter import SqlHighlighter

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def highlighter():
    """
    Crea una instancia del resaltador SQL asociada
    a un documento de texto.
    """

    document = QTextDocument()

    return SqlHighlighter(document)


@pytest.fixture
def mocked_highlighter(highlighter):
    """
    Devuelve un resaltador SQL con los métodos de Qt
    utilizados durante el resaltado reemplazados por
    objetos MagicMock para facilitar su verificación.
    """

    highlighter.setFormat = MagicMock()
    highlighter.previousBlockState = MagicMock(return_value=0)
    highlighter.setCurrentBlockState = MagicMock()
    return highlighter


# =============================================================================
# FORMAT CREATION
# =============================================================================


@pytest.mark.parametrize(
    "rule, is_bold",
    [
        (
            {"color": "sql_keyword_color"},
            False,
        ),
        (
            {
                "color": "sql_keyword_color",
                "bold": True,
            },
            True,
        ),
    ],
)
def test_create_format(
    highlighter,
    monkeypatch,
    rule,
    is_bold,
):
    """
    Verifica que _create_format crea un QTextCharFormat
    y aplica correctamente el peso de la fuente según
    la configuración de la regla.
    """

    monkeypatch.setattr(
        "ui.themes.theme_manager.ThemeManager.get_color",
        lambda _: "#ffffff",
    )

    fmt = highlighter._create_format(rule)

    assert isinstance(fmt, QTextCharFormat)

    expected = QFont.Weight.Bold if is_bold else QFont.Weight.Normal

    assert fmt.fontWeight() == expected


# =============================================================================
# RULE REGISTRATION
# =============================================================================


@pytest.mark.parametrize(
    "protected, attr",
    [
        (
            False,
            "rules",
        ),
        (
            True,
            "protected_rules",
        ),
    ],
)
def test_add_rule(
    highlighter,
    protected,
    attr,
):
    """
    Verifica que _add_rule registra la regla en la
    colección correspondiente según su tipo.
    """

    before = len(getattr(highlighter, attr))

    highlighter._add_rule(
        {
            "color": "sql_keyword_color",
            "patterns": [r"\bTEST\b"],
            "protected": protected,
        }
    )

    assert len(getattr(highlighter, attr)) == before + 1


def test_register_rules_loads_all_rules(
    highlighter,
):
    """
    Verifica que el constructor registra reglas.
    """

    assert highlighter.rules
    assert highlighter.protected_rules


# =============================================================================
# HIGHLIGHT HELPERS
# =============================================================================

# =====================================
# IS PROTECTED
# =====================================


@pytest.mark.parametrize(
    (
        "start",
        "end",
        "protected_ranges",
        "expected",
    ),
    [
        (5, 10, [], False),
        (5, 10, [(0, 4)], False),
        (5, 10, [(6, 8)], True),
        (5, 10, [(0, 6)], True),
        (5, 10, [(9, 15)], True),
        (5, 10, [(5, 10)], True),
    ],
)
def test_is_protected(
    start,
    end,
    protected_ranges,
    expected,
):
    """
    Verifica que _is_protected detecta correctamente
    si un rango pertenece a una zona protegida.
    """

    assert (
        SqlHighlighter._is_protected(
            start,
            end,
            protected_ranges,
        )
        is expected
    )


# =====================================
# PROTECTED RULES
# =====================================


@pytest.mark.parametrize(
    "protected, expected_calls, expected_ranges",
    [
        (
            [],
            1,
            [(0, 7)],
        ),
        (
            [(0, 7)],
            0,
            [(0, 7)],
        ),
    ],
)
def test_highlight_protected_rules(
    highlighter,
    protected,
    expected_calls,
    expected_ranges,
):
    """
    Verifica que las reglas protegidas aplican formato
    únicamente cuando la coincidencia no pertenece a un
    rango protegido existente.
    """

    pattern = QRegularExpression(r"'[^']*'")
    fmt = QTextCharFormat()

    highlighter.protected_rules = [(pattern, fmt)]
    highlighter.setFormat = MagicMock()

    highlighter._highlight_protected_rules(
        "'hello'",
        protected,
    )

    assert protected == expected_ranges
    assert highlighter.setFormat.call_count == expected_calls


# =====================================
# STANDARD RULES
# =====================================


@pytest.mark.parametrize(
    "protected, called",
    [
        ([], True),
        ([(0, 6)], False),
    ],
)
def test_highlight_standard_rules(
    highlighter,
    protected,
    called,
):
    """
    Verifica que las reglas estándar sólo aplican
    formato sobre regiones que no están protegidas.
    """

    highlighter.setFormat = MagicMock()

    highlighter._highlight_standard_rules(
        "SELECT",
        protected,
    )

    assert highlighter.setFormat.called is called


# =====================================
# MULTILINE COMMENTS
# =====================================


@pytest.mark.parametrize(
    (
        "text",
        "previous_state",
        "expected_state",
    ),
    [
        ("/* comentario", 0, SqlHighlighter.MULTILINE_COMMENT),
        ("comentario */", SqlHighlighter.MULTILINE_COMMENT, 0),
        ("/* comentario */", 0, 0),
        ("SELECT 1", 0, 0),
    ],
)
def test_highlight_multiline_comments_sets_block_state(
    mocked_highlighter,
    text,
    previous_state,
    expected_state,
):
    """
    Verifica que el estado del bloque se actualiza
    correctamente para comentarios multilínea.
    """

    protected = []

    mocked_highlighter.previousBlockState.return_value = previous_state

    mocked_highlighter._highlight_multiline_comments(
        text,
        protected,
    )

    mocked_highlighter.setCurrentBlockState.assert_called_with(
        expected_state,
    )


def test_highlight_multiline_comments_adds_protected_range(
    mocked_highlighter,
):
    """
    Verifica que un comentario multilínea añade un
    rango protegido.
    """

    protected = []

    mocked_highlighter._highlight_multiline_comments(
        "/* hola */",
        protected,
    )

    assert len(protected) == 1

    mocked_highlighter.setFormat.assert_called_once()


def test_highlight_multiline_comments_without_comment(
    mocked_highlighter,
):
    """
    Verifica que no se aplica formato cuando el bloque
    no contiene comentarios multilínea.
    """

    protected = []

    mocked_highlighter._highlight_multiline_comments(
        "SELECT 1;",
        protected,
    )

    assert protected == []

    mocked_highlighter.setFormat.assert_not_called()


# =============================================================================
# HIGHLIGHT BLOCK
# =============================================================================


def test_highlight_block_calls_internal_helpers(
    highlighter,
):
    """
    Verifica que highlightBlock ejecuta sus tres fases
    principales de resaltado.
    """

    highlighter._highlight_multiline_comments = MagicMock()
    highlighter._highlight_protected_rules = MagicMock()
    highlighter._highlight_standard_rules = MagicMock()

    highlighter.highlightBlock("SELECT 1")

    highlighter._highlight_multiline_comments.assert_called_once()
    highlighter._highlight_protected_rules.assert_called_once()
    highlighter._highlight_standard_rules.assert_called_once()


# =============================================================================
# PUBLIC API
# =============================================================================


def test_reload_theme_clears_rules(monkeypatch, highlighter):
    """
    Verifica que reload_theme elimina las reglas
    existentes antes de reconstruirlas.
    """

    highlighter.rules = [MagicMock()]
    highlighter.protected_rules = [MagicMock()]

    register = MagicMock()
    rehighlight = MagicMock()

    monkeypatch.setattr(
        highlighter,
        "_register_rules",
        register,
    )

    monkeypatch.setattr(
        highlighter,
        "rehighlight",
        rehighlight,
    )

    highlighter.reload_theme()

    assert highlighter.rules == []
    assert highlighter.protected_rules == []

    register.assert_called_once()
    rehighlight.assert_called_once()


def test_reload_theme_calls_register_rules(monkeypatch, highlighter):
    """
    Verifica que reload_theme reconstruye las
    reglas de resaltado.
    """

    register = MagicMock()

    monkeypatch.setattr(
        highlighter,
        "_register_rules",
        register,
    )

    monkeypatch.setattr(
        highlighter,
        "rehighlight",
        MagicMock(),
    )

    highlighter.reload_theme()

    register.assert_called_once()


def test_reload_theme_rehighlights_document(monkeypatch, highlighter):
    """
    Verifica que reload_theme fuerza el
    rehighlight del documento.
    """

    monkeypatch.setattr(
        highlighter,
        "_register_rules",
        MagicMock(),
    )

    rehighlight = MagicMock()

    monkeypatch.setattr(
        highlighter,
        "rehighlight",
        rehighlight,
    )

    highlighter.reload_theme()

    rehighlight.assert_called_once()

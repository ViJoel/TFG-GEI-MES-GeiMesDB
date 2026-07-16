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
# FIXTURE
# =============================================================================


@pytest.fixture
def highlighter():
    """
    Crea una instancia del resaltador SQL asociada
    a un documento de texto.
    """

    document = QTextDocument()

    return SqlHighlighter(document)


# =============================================================================
# FORMAT CREATION
# =============================================================================


def test_create_format_returns_qtextcharformat(
    highlighter,
    monkeypatch,
):
    """
    Verifica que _create_format genera un QTextCharFormat.
    """

    monkeypatch.setattr(
        "ui.themes.theme_manager.ThemeManager.get_color",
        lambda _: "#ffffff",
    )

    fmt = highlighter._create_format(
        {
            "color": "sql_keyword_color",
        }
    )

    assert isinstance(
        fmt,
        QTextCharFormat,
    )


def test_create_format_applies_bold(
    highlighter,
    monkeypatch,
):
    """
    Verifica que las reglas con bold generan fuente negrita.
    """

    monkeypatch.setattr(
        "ui.themes.theme_manager.ThemeManager.get_color",
        lambda _: "#ffffff",
    )

    fmt = highlighter._create_format(
        {
            "color": "sql_keyword_color",
            "bold": True,
        }
    )

    assert fmt.fontWeight() == QFont.Weight.Bold


def test_create_format_default_not_bold(
    highlighter,
    monkeypatch,
):
    monkeypatch.setattr(
        "ui.themes.theme_manager.ThemeManager.get_color",
        lambda _: "#ffffff",
    )

    fmt = highlighter._create_format(
        {
            "color": "sql_keyword_color",
        }
    )

    assert fmt.fontWeight() != QFont.Weight.Bold


# =============================================================================
# RULE REGISTRATION
# =============================================================================


def test_add_rule_registers_normal_rule(
    highlighter,
):
    """
    Comprueba que una regla normal entra en rules.
    """

    rule = {
        "color": "sql_keyword_color",
        "patterns": [
            r"\bTEST\b",
        ],
    }

    rules_before = len(highlighter.rules)

    highlighter._add_rule(rule)

    assert len(highlighter.rules) == rules_before + 1


def test_add_rule_registers_protected_rule(
    highlighter,
):
    rule = {
        "color": "sql_string_color",
        "patterns": [
            r"'[^']*'",
        ],
        "protected": True,
    }

    before = len(highlighter.protected_rules)

    highlighter._add_rule(rule)

    assert len(highlighter.protected_rules) == before + 1


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


def test_highlight_protected_rules_calls_set_format(
    highlighter,
):
    """
    Verifica que las reglas protegidas aplican formato
    y registran los rangos protegidos.
    """

    protected_ranges = []

    highlighter.setFormat = MagicMock()

    highlighter._highlight_protected_rules(
        "'hola'",
        protected_ranges,
    )

    assert protected_ranges
    highlighter.setFormat.assert_called()


def test_highlight_standard_rules_calls_set_format(
    highlighter,
):
    """
    Verifica que las reglas normales aplican formato
    cuando el texto no pertenece a un rango protegido.
    """

    highlighter.setFormat = MagicMock()

    highlighter._highlight_standard_rules(
        "SELECT 1",
        [],
    )

    highlighter.setFormat.assert_called()


def test_highlight_standard_rules_skips_protected_ranges(
    highlighter,
):
    """
    Verifica que las reglas normales no sobrescriben
    texto perteneciente a un rango protegido.
    """

    highlighter.setFormat = MagicMock()

    protected = [
        (
            0,
            len("SELECT"),
        )
    ]

    highlighter._highlight_standard_rules(
        "SELECT",
        protected,
    )

    highlighter.setFormat.assert_not_called()


def test_highlight_protected_rules_continues_when_range_is_already_protected(
    highlighter,
):
    """
    Verifica que una coincidencia dentro de un rango ya protegido
    se ignora y no aplica formato.
    """

    pattern = QRegularExpression(
        r"'[^']*'",
    )

    fmt = QTextCharFormat()

    highlighter.protected_rules = [
        (
            pattern,
            fmt,
        )
    ]

    highlighter.setFormat = MagicMock()

    protected_ranges = [
        (
            0,
            7,
        )
    ]

    highlighter._highlight_protected_rules(
        "'hello'",
        protected_ranges,
    )

    highlighter.setFormat.assert_not_called()

    # El rango existente no debe duplicarse
    assert protected_ranges == [
        (
            0,
            7,
        )
    ]


def test_highlight_protected_rules_adds_new_range(
    highlighter,
):
    """
    Verifica que una coincidencia nueva se añade
    y se formatea.
    """

    pattern = QRegularExpression(
        r"'[^']*'",
    )

    fmt = QTextCharFormat()

    highlighter.protected_rules = [
        (
            pattern,
            fmt,
        )
    ]

    highlighter.setFormat = MagicMock()

    protected_ranges = []

    highlighter._highlight_protected_rules(
        "'hello'",
        protected_ranges,
    )

    assert protected_ranges == [
        (
            0,
            7,
        )
    ]

    highlighter.setFormat.assert_called_once_with(
        0,
        7,
        fmt,
    )


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
    highlighter,
    text,
    previous_state,
    expected_state,
):
    """
    Verifica que el estado del bloque se actualiza
    correctamente para comentarios multilínea.
    """

    protected = []

    highlighter.previousBlockState = MagicMock(
        return_value=previous_state,
    )
    highlighter.setCurrentBlockState = MagicMock()
    highlighter.setFormat = MagicMock()

    highlighter._highlight_multiline_comments(
        text,
        protected,
    )

    highlighter.setCurrentBlockState.assert_called_with(
        expected_state,
    )


def test_highlight_multiline_comments_adds_protected_range(
    highlighter,
):
    """
    Verifica que un comentario multilínea añade un
    rango protegido.
    """

    protected = []

    highlighter.previousBlockState = MagicMock(
        return_value=0,
    )
    highlighter.setCurrentBlockState = MagicMock()
    highlighter.setFormat = MagicMock()

    highlighter._highlight_multiline_comments(
        "/* hola */",
        protected,
    )

    assert len(protected) == 1
    highlighter.setFormat.assert_called_once()


def test_highlight_multiline_comments_without_comment(
    highlighter,
):
    """
    Verifica que no se aplica formato cuando el bloque
    no contiene comentarios multilínea.
    """

    protected = []

    highlighter.previousBlockState = MagicMock(
        return_value=0,
    )
    highlighter.setCurrentBlockState = MagicMock()
    highlighter.setFormat = MagicMock()

    highlighter._highlight_multiline_comments(
        "SELECT 1;",
        protected,
    )

    assert protected == []
    highlighter.setFormat.assert_not_called()


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

import re
from unittest.mock import MagicMock

import pytest
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
# RULES SETUP
# =============================================================================


@pytest.mark.parametrize(
    ("color_key", "bold"),
    [
        ("sql_keyword_color", False),
        ("sql_keyword_color", True),
    ],
)
def test_create_format_returns_expected_format(
    highlighter,
    color_key,
    bold,
):
    """
    Verifica que _create_format devuelve un QTextCharFormat
    correctamente configurado.
    """

    fmt = highlighter._create_format(
        color_key,
        bold,
    )

    assert isinstance(fmt, QTextCharFormat)

    expected = QFont.Weight.Bold if bold else QFont.Weight.Normal

    assert fmt.fontWeight() == expected


@pytest.mark.parametrize(
    "protected",
    [
        False,
        True,
    ],
)
def test_add_rule_adds_rule_to_expected_collection(
    highlighter,
    protected,
):
    """
    Verifica que _add_rule añade la regla a la colección
    correspondiente.
    """

    rule = r"\bTEST\b"
    fmt = QTextCharFormat()

    protected_before = len(highlighter.protected_rules)
    rules_before = len(highlighter.rules)

    highlighter._add_rule(
        rule,
        fmt,
        protected=protected,
    )

    if protected:
        assert len(highlighter.protected_rules) == protected_before + 1
        assert len(highlighter.rules) == rules_before
    else:
        assert len(highlighter.rules) == rules_before + 1
        assert len(highlighter.protected_rules) == protected_before


def test_build_word_pattern():
    """
    Verifica que _build_word_pattern genera una expresión
    regular para palabras completas.
    """

    pattern = SqlHighlighter._build_word_pattern(
        {
            "SELECT",
            "FROM",
        }
    )

    regex = re.compile(pattern)

    assert regex.search("SELECT")
    assert regex.search("FROM")
    assert not regex.search("SELECTED")


def test_build_symbol_pattern():
    """
    Verifica que _build_symbol_pattern construye
    correctamente el patrón de símbolos y prioriza
    los operadores más largos.
    """

    pattern = SqlHighlighter._build_symbol_pattern(
        {
            ">",
            ">=",
            "=",
            "+",
        }
    )

    tokens = pattern.removeprefix("(").removesuffix(")").split("|")

    assert tokens.index(">=") < tokens.index(">")
    assert "=" in tokens
    assert r"\+" in tokens


# =============================================================================
# RULE CREATION
# =============================================================================


@pytest.mark.parametrize(
    (
        "method_name",
        "protected_count",
        "rules_count",
    ),
    [
        ("_create_string_rules", 1, 0),
        ("_create_comment_rules", 1, 0),
        ("_create_keyword_rules", 0, 1),
        ("_create_type_rules", 0, 1),
        ("_create_function_rules", 0, 1),
        ("_create_literal_rules", 0, 3),
        ("_create_symbol_rules", 0, 1),
        ("_create_parameter_rules", 0, 3),
        ("_create_variable_rules", 0, 2),
        ("_create_identifier_rules", 3, 0),
    ],
)
def test_create_rules_add_expected_number_of_rules(
    method_name,
    protected_count,
    rules_count,
):
    highlighter = SqlHighlighter(QTextDocument())

    highlighter.protected_rules.clear()
    highlighter.rules.clear()

    getattr(highlighter, method_name)()

    assert len(highlighter.protected_rules) == protected_count
    assert len(highlighter.rules) == rules_count


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

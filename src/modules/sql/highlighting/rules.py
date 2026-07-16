import re

from modules.sql.syntax.ansi.functions import SQL_FUNCTIONS
from modules.sql.syntax.ansi.keywords import SQL_KEYWORDS
from modules.sql.syntax.ansi.literals import (
    SQL_BOOLEAN_VALUES,
    SQL_NULL_VALUES,
)
from modules.sql.syntax.ansi.symbols import SQL_SYMBOLS
from modules.sql.syntax.ansi.types import SQL_TYPES


def build_word_pattern(
    words: set[str],
) -> str:
    """
    Construye una expresión regular para
    palabras completas.

    Args:
        words (set[str]):
            Palabras que forman parte de la regla.

    Returns:
        str:
            Patrón regex generado.
    """

    escaped = map(re.escape, sorted(words))

    return rf"\b({'|'.join(escaped)})\b"


def build_symbol_pattern(
    symbols: set[str],
) -> str:
    """
    Construye una expresión regular para
    operadores y símbolos SQL.

    Args:
        symbols (set[str]):
            Símbolos que forman parte de la regla.

    Returns:
        str:
            Patrón regex generado.
    """

    escaped = sorted(
        (re.escape(symbol) for symbol in symbols),
        key=len,
        reverse=True,
    )

    return f"({'|'.join(escaped)})"


def build_function_pattern(
    words: set[str],
) -> str:
    """
    Construye una expresión regular para
    funciones SQL.

    Args:
        words (set[str]):
            Palabras que forman parte de la regla.

    Returns:
        str:
            Patrón regex generado.
    """

    escaped = map(re.escape, sorted(words))

    return rf"\b({'|'.join(escaped)})\b(?=\s*\()"


SQL_HIGHLIGHT_RULES = {
    # =================
    # === Estáticos ===
    # =================
    "boolean": {
        "color": "sql_boolean_color",
        "patterns": [],
        "patterns_builder": build_word_pattern,
        "values": SQL_BOOLEAN_VALUES,
    },
    "comments": {
        "color": "sql_comment_color",
        "patterns": [
            r"--[^\n]*",
        ],
        "protected": True,
    },
    "functions": {
        "color": "sql_function_color",
        "patterns": [],
        "patterns_builder": build_function_pattern,
        "values": SQL_FUNCTIONS,
    },
    "identifiers": {
        "color": "sql_identifier_color",
        "patterns": [
            r'"[^"]*"',
            r"`[^`]*`",
            r"\[[^\]]+\]",
        ],
        "protected": True,
    },
    "keywords": {
        "bold": True,
        "color": "sql_keyword_color",
        "patterns": [],
        "patterns_builder": build_word_pattern,
        "protected": False,
        "values": SQL_KEYWORDS,
    },
    "null": {
        "color": "sql_null_color",
        "patterns": [],
        "patterns_builder": build_word_pattern,
        "values": SQL_NULL_VALUES,
    },
    "numbers": {
        "color": "sql_number_color",
        "patterns": [
            r"\b\d+(\.\d+)?\b",
        ],
    },
    "parameters": {
        "color": "sql_parameter_color",
        "patterns": [
            r":[A-Za-z_]\w*",
            r"\$\d+",
            r"\?",
        ],
    },
    "strings": {
        "color": "sql_string_color",
        "patterns": [
            r"'[^']*'",
        ],
        "protected": True,
    },
    "symbols": {
        "color": "sql_symbol_color",
        "patterns": [],
        "patterns_builder": build_symbol_pattern,
        "values": SQL_SYMBOLS,
    },
    "types": {
        "color": "sql_type_color",
        "patterns": [],
        "patterns_builder": build_word_pattern,
        "protected": False,
        "values": SQL_TYPES,
    },
    "variables": {
        "color": "sql_variable_color",
        "patterns": [
            r"@[A-Za-z_]\w*",
            r"@@[A-Za-z_]\w*",
        ],
    },
}


def _compile_rules() -> None:
    """
    Compila automáticamente los patrones
    generados a partir de los valores.
    """

    for rule in SQL_HIGHLIGHT_RULES.values():

        builder = rule.get("patterns_builder")

        if builder is None:
            continue

        rule["patterns"] = [
            builder(rule["values"]),
        ]


_compile_rules()

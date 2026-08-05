import re

from modules.sql.syntax.ansi.functions import SQL_FUNCTIONS
from modules.sql.syntax.ansi.keywords import SQL_KEYWORDS
from modules.sql.syntax.ansi.literals import (
    SQL_BOOLEAN_VALUES,
    SQL_CONSTANTS,
    SQL_NULL_VALUES,
)
from modules.sql.syntax.ansi.symbols import SQL_SYMBOLS
from modules.sql.syntax.ansi.types import SQL_TYPES
from modules.sql.theme.colors import (
    DEFAULT_COLOR,
    SQL_THEME_COLORS,
)


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
    "booleans": {
        "patterns": [],
        "patterns_builder": build_word_pattern,
        "values": SQL_BOOLEAN_VALUES,
    },
    "comments": {
        "patterns": [
            r"--[^\n]*",
        ],
        "protected": True,
    },
    "constants": {
        "patterns": [],
        "patterns_builder": build_word_pattern,
        "values": SQL_CONSTANTS,
    },
    "functions": {
        "patterns": [],
        "patterns_builder": build_function_pattern,
        "values": SQL_FUNCTIONS,
    },
    "identifiers": {
        "patterns": [
            r'"[^"]*"',
            r"`[^`]*`",
            r"\[[^\]]+\]",
        ],
        "protected": True,
    },
    "keywords": {
        "bold": True,
        "patterns": [],
        "patterns_builder": build_word_pattern,
        "protected": False,
        "values": SQL_KEYWORDS,
    },
    "nulls": {
        "patterns": [],
        "patterns_builder": build_word_pattern,
        "values": SQL_NULL_VALUES,
    },
    "numbers": {
        "patterns": [
            r"\b\d+(\.\d+)?\b",
        ],
    },
    "parameters": {
        "patterns": [
            r":\w*",
            r"\$\d+",
            r"\?",
        ],
    },
    "strings": {
        "patterns": [
            r"'[^']*'",
        ],
        "protected": True,
    },
    "symbols": {
        "patterns": [],
        "patterns_builder": build_symbol_pattern,
        "values": SQL_SYMBOLS,
    },
    "types": {
        "patterns": [],
        "patterns_builder": build_word_pattern,
        "protected": False,
        "values": SQL_TYPES,
    },
    "variables": {
        "patterns": [
            r"@@?\w*",
        ],
    },
}


def _compile_rules() -> None:
    """
    Compila automáticamente los patrones
    generados a partir de los valores.
    """

    for category, rule in SQL_HIGHLIGHT_RULES.items():

        # 1. Extrae el color usando el nombre de la clave.
        #    Si no existe, usa DEFAULT_COLOR
        rule["color"] = SQL_THEME_COLORS.get(
            category,
            DEFAULT_COLOR,
        )

        # 2. Lógica de compilación
        builder = rule.get("patterns_builder")

        if builder is not None:
            rule["patterns"] = [
                builder(rule["values"]),
            ]


# Ejecutamos la configuración e inyección al cargar el módulo
_compile_rules()

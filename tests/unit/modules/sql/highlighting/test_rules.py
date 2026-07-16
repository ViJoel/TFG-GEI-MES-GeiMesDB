import re

import pytest

from modules.sql.highlighting.rules import (
    SQL_HIGHLIGHT_RULES,
    _compile_rules,
    build_function_pattern,
    build_symbol_pattern,
    build_word_pattern,
)

# ============================================================
# build_word_pattern
# ============================================================


def test_build_word_pattern_creates_complete_word_regex():
    pattern = build_word_pattern({"SELECT", "FROM"})

    regex = re.compile(pattern, re.IGNORECASE)

    assert regex.search("SELECT")
    assert regex.search("FROM")


def test_build_word_pattern_does_not_match_partial_words():
    pattern = build_word_pattern({"SELECT"})

    regex = re.compile(pattern)

    assert regex.search("SELECT")

    assert regex.search("MYSELECT") is None
    assert regex.search("SELECTED") is None


def test_build_word_pattern_escapes_special_characters():
    pattern = build_word_pattern({"A+B"})

    regex = re.compile(pattern)

    assert regex.search("A+B")
    assert regex.search("AAB") is None


def test_build_word_pattern_orders_words():
    pattern = build_word_pattern(
        {
            "FROM",
            "SELECT",
            "WHERE",
        }
    )

    assert pattern.startswith(r"\b(")


# ============================================================
# build_symbol_pattern
# ============================================================


def test_build_symbol_pattern_matches_symbols():
    pattern = build_symbol_pattern(
        {
            "+",
            "-",
            "*",
        }
    )

    regex = re.compile(pattern)

    assert regex.search("+")
    assert regex.search("-")
    assert regex.search("*")


def test_build_symbol_pattern_escapes_regex_symbols():
    pattern = build_symbol_pattern(
        {
            ".",
            "*",
            "+",
        }
    )

    regex = re.compile(pattern)

    assert regex.search(".")
    assert regex.search("*")
    assert regex.search("+")


def test_build_symbol_pattern_matches_longer_symbol_first():
    pattern = build_symbol_pattern(
        {
            "=",
            "==",
        }
    )

    regex = re.compile(pattern)

    match = regex.search("==")

    assert match.group() == "=="


# ============================================================
# build_function_pattern
# ============================================================


def test_build_function_pattern_requires_parenthesis():
    pattern = build_function_pattern(
        {
            "COUNT",
            "SUM",
        }
    )

    regex = re.compile(pattern, re.IGNORECASE)

    assert regex.search("COUNT(value)")
    assert regex.search("SUM(value)")


def test_build_function_pattern_does_not_match_identifier():
    pattern = build_function_pattern(
        {
            "COUNT",
        }
    )

    regex = re.compile(pattern)

    assert regex.search("COUNT(value)")
    assert regex.search("COUNT") is None


def test_build_function_pattern_allows_spaces_before_parenthesis():
    pattern = build_function_pattern(
        {
            "COUNT",
        }
    )

    regex = re.compile(pattern)

    assert regex.search("COUNT   (value)")


# ============================================================
# _compile_rules
# ============================================================


def test_compile_rules_builds_patterns():
    rules_before = {
        key: value["patterns"].copy() for key, value in SQL_HIGHLIGHT_RULES.items()
    }

    _compile_rules()

    for rule in SQL_HIGHLIGHT_RULES.values():

        if "patterns_builder" in rule:
            assert rule["patterns"]


def test_compile_rules_does_not_modify_static_patterns():
    _compile_rules()

    assert r"--[^\n]*" in SQL_HIGHLIGHT_RULES["comments"]["patterns"]

    assert r"'[^']*'" in SQL_HIGHLIGHT_RULES["strings"]["patterns"]


# ============================================================
# SQL_HIGHLIGHT_RULES structure
# ============================================================


@pytest.mark.parametrize(
    "rule_name",
    [
        "boolean",
        "comments",
        "functions",
        "identifiers",
        "keywords",
        "null",
        "numbers",
        "parameters",
        "strings",
        "symbols",
        "types",
        "variables",
    ],
)
def test_all_highlight_rules_exist(rule_name):
    assert rule_name in SQL_HIGHLIGHT_RULES


def test_rules_with_builder_have_values():
    for rule in SQL_HIGHLIGHT_RULES.values():

        if "patterns_builder" in rule:
            assert rule["values"]


def test_protected_rules_are_marked():
    protected_rules = {
        "comments",
        "identifiers",
        "strings",
    }

    for name in protected_rules:
        assert SQL_HIGHLIGHT_RULES[name]["protected"] is True

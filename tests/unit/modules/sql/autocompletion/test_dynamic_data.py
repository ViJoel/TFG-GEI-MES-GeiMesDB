import pytest

from modules.sql.autocompletion.dynamic_data import SqlDynamicCompletionData
from modules.sql.theme.colors import (
    DEFAULT_COLOR,
    SQL_THEME_COLORS,
)


def test_init_initializes_category_colors():
    """
    Verifica que todas las categorías dinámicas
    reciben un color durante la inicialización.
    """

    data = SqlDynamicCompletionData()

    for category, value in data.get_data().items():

        assert value["color"] == SQL_THEME_COLORS.get(
            category,
            DEFAULT_COLOR,
        )


def test_get_data_returns_internal_dictionary():
    """
    Verifica que get_data devuelve el
    diccionario interno.
    """

    data = SqlDynamicCompletionData()

    assert data.get_data() is data.data


def test_clear_dynamic_completion_data_removes_all_values():
    """
    Verifica que se eliminan todos los valores
    de las categorías dinámicas.
    """

    data = SqlDynamicCompletionData()

    data.update_dynamic_completion_data(
        "parameters",
        {"p1"},
    )

    data.update_dynamic_completion_data(
        "variables",
        {"v1"},
    )

    data.clear_dynamic_completion_data()

    assert data.data["parameters"]["values"] == set()
    assert data.data["variables"]["values"] == set()


def test_update_dynamic_completion_data_adds_values():
    """
    Verifica que los valores se añaden a la
    categoría indicada.
    """

    data = SqlDynamicCompletionData()

    data.update_dynamic_completion_data(
        "parameters",
        {"a", "b"},
    )

    assert data.data["parameters"]["values"] == {"a", "b"}


def test_has_changes_returns_true_when_values_are_different():
    """
    Verifica que devuelve True cuando existen
    diferencias.
    """

    data = SqlDynamicCompletionData()

    assert data.has_changes(
        "parameters",
        {"a"},
    )


def test_has_changes_returns_false_when_values_are_equal():
    """
    Verifica que devuelve False cuando los
    valores coinciden.
    """

    data = SqlDynamicCompletionData()

    data.update_dynamic_completion_data(
        "parameters",
        {"a"},
    )

    assert not data.has_changes(
        "parameters",
        {"a"},
    )


def test_initialize_dynamic_data_uses_default_color():
    """
    Verifica que se utiliza DEFAULT_COLOR cuando
    la categoría no tiene color definido.
    """

    data = SqlDynamicCompletionData()

    data.data = {
        "unknown": {
            "values": set(),
        },
    }

    data._initialize_dynamic_data()

    assert data.data["unknown"]["color"] == DEFAULT_COLOR

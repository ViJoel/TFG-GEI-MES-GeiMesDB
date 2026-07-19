from modules.sql.autocompletion import static_data
from modules.sql.autocompletion.static_data import (
    SQL_STATIC_COMPLETION_DATA,
)
from modules.sql.theme.colors import (
    DEFAULT_COLOR,
    SQL_THEME_COLORS,
)


def test_initialize_static_data_assigns_color_to_all_categories():
    """
    Verifica que todas las categorías reciben un color
    durante la inicialización del módulo.
    """

    for category, data in SQL_STATIC_COMPLETION_DATA.items():

        assert "color" in data

        assert data["color"] == SQL_THEME_COLORS.get(
            category,
            DEFAULT_COLOR,
        )


def test_initialize_static_data_uses_default_color(monkeypatch):
    """
    Verifica que se utiliza DEFAULT_COLOR cuando una
    categoría no tiene color definido.
    """

    monkeypatch.setattr(
        static_data,
        "SQL_STATIC_COMPLETION_DATA",
        {
            "unknown": {
                "values": [],
            },
        },
    )

    static_data._initialize_static_data()

    assert (
        static_data.SQL_STATIC_COMPLETION_DATA["unknown"]["color"]
        == static_data.DEFAULT_COLOR
    )

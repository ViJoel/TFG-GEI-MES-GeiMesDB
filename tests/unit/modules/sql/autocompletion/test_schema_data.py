import pytest

from modules.sql.autocompletion.schema_data import SqlSchemaCompletionData
from modules.sql.theme.colors import (
    DEFAULT_COLOR,
    SQL_THEME_COLORS,
)

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def schema_data():
    """
    Instancia limpia del almacén de datos
    del esquema SQL.
    """

    return SqlSchemaCompletionData()


# =============================================================================
# INIT
# =============================================================================


def test_init_creates_all_schema_categories(
    schema_data,
):
    """
    Verifica que la inicialización crea todas las
    categorías esperadas del esquema.
    """

    data = schema_data.get_data()

    assert set(data.keys()) == {
        "tables",
        "views",
        "columns",
        "constraints",
        "indexes",
    }


def test_init_initializes_all_categories_with_empty_values(
    schema_data,
):
    """
    Verifica que todas las categorías comienzan
    sin elementos almacenados.
    """

    for category in schema_data.get_data().values():
        assert category["values"] == set()


def test_init_assigns_category_colors(
    schema_data,
):
    """
    Verifica que cada categoría recibe el color
    configurado en el tema SQL.
    """

    data = schema_data.get_data()

    for category, values in data.items():

        assert values["color"] == SQL_THEME_COLORS.get(
            category,
            DEFAULT_COLOR,
        )


# =============================================================================
# GET DATA
# =============================================================================


def test_get_data_returns_internal_dictionary(
    schema_data,
):
    """
    Verifica que get_data devuelve el diccionario
    interno del almacén.
    """

    assert schema_data.get_data() is schema_data.data


# =============================================================================
# CLEAR
# =============================================================================


def test_clear_removes_all_values(
    schema_data,
):
    """
    Verifica que clear elimina todos los valores
    almacenados en cada categoría.
    """

    schema_data.update(
        {
            "tables": ["users"],
            "views": ["active_users"],
            "columns": ["id", "name"],
            "constraints": ["pk_users"],
            "indexes": ["idx_users"],
        }
    )

    schema_data.clear()

    for category in schema_data.get_data().values():
        assert category["values"] == set()


def test_clear_preserves_category_colors(
    schema_data,
):
    """
    Verifica que clear no modifica los colores
    asociados a las categorías.
    """

    expected_colors = {
        category: values["color"] for category, values in schema_data.get_data().items()
    }

    schema_data.update(
        {
            "tables": ["users"],
            "columns": ["id"],
        }
    )

    schema_data.clear()

    for category, values in schema_data.get_data().items():
        assert values["color"] == expected_colors[category]


# =============================================================================
# UPDATE
# =============================================================================


def test_update_replaces_existing_completion_data(
    schema_data,
):
    """
    Verifica que update sustituye completamente
    los datos almacenados previamente.
    """

    schema_data.update(
        {
            "tables": ["old_table"],
            "columns": ["old_column"],
        }
    )

    schema_data.update(
        {
            "tables": ["users"],
            "views": ["active_users"],
            "columns": ["id", "name"],
            "constraints": ["pk_users"],
            "indexes": ["idx_users"],
        }
    )

    data = schema_data.get_data()

    assert data["tables"]["values"] == {"users"}
    assert data["views"]["values"] == {"active_users"}
    assert data["columns"]["values"] == {"id", "name"}
    assert data["constraints"]["values"] == {"pk_users"}
    assert data["indexes"]["values"] == {"idx_users"}


def test_update_keeps_empty_categories_when_not_provided(
    schema_data,
):
    """
    Verifica que las categorías no incluidas en la
    actualización permanecen vacías.
    """

    schema_data.update(
        {
            "tables": ["users"],
        }
    )

    data = schema_data.get_data()

    assert data["tables"]["values"] == {"users"}
    assert data["views"]["values"] == set()
    assert data["columns"]["values"] == set()
    assert data["constraints"]["values"] == set()
    assert data["indexes"]["values"] == set()


def test_update_removes_previous_values(
    schema_data,
):
    """
    Verifica que update elimina los valores
    anteriores antes de cargar los nuevos.
    """

    schema_data.update(
        {
            "tables": ["users"],
        }
    )

    schema_data.update(
        {
            "tables": ["products"],
        }
    )

    assert schema_data.get_data()["tables"]["values"] == {
        "products",
    }


def test_update_ignores_duplicate_values(
    schema_data,
):
    """
    Verifica que los valores duplicados se almacenan
    una única vez al utilizar conjuntos.
    """

    schema_data.update(
        {
            "tables": [
                "users",
                "users",
                "users",
            ],
        }
    )

    assert schema_data.get_data()["tables"]["values"] == {
        "users",
    }


def test_update_preserves_category_colors(
    schema_data,
):
    """
    Verifica que actualizar los valores no modifica
    los colores asociados a las categorías.
    """

    expected_colors = {
        category: values["color"] for category, values in schema_data.get_data().items()
    }

    schema_data.update(
        {
            "tables": ["users"],
            "columns": ["id"],
        }
    )

    for category, values in schema_data.get_data().items():
        assert values["color"] == expected_colors[category]

import pytest

from entities.unsaved_changes_count import UnsavedChangesCount

# =============================================================================
# TESTS
# =============================================================================


def test_create_unsaved_changes_count():
    """
    Comprueba que crea correctamente la entidad de cambios no guardados.
    """

    entity = UnsavedChangesCount(
        connection_name="main",
        unsaved_changes=3,
    )

    assert entity.connection_name == "main"
    assert entity.unsaved_changes == 3


def test_unsaved_changes_count_requires_keyword_arguments():
    """
    Comprueba que la entidad requiere argumentos nombrados.
    """

    with pytest.raises(TypeError):
        UnsavedChangesCount("main", 3)


def test_unsaved_changes_count_accepts_zero_changes():
    """
    Comprueba que acepta una cantidad de cambios no guardados igual a cero.
    """

    entity = UnsavedChangesCount(
        connection_name="main",
        unsaved_changes=0,
    )

    assert entity.unsaved_changes == 0


def test_unsaved_changes_count_accepts_multiple_connections():
    """
    Comprueba que permite almacenar cambios no guardados de varias conexiones.
    """

    entities = [
        UnsavedChangesCount(
            connection_name="connection_1",
            unsaved_changes=2,
        ),
        UnsavedChangesCount(
            connection_name="connection_2",
            unsaved_changes=5,
        ),
    ]

    assert entities[0].connection_name == "connection_1"
    assert entities[1].unsaved_changes == 5


def test_two_entities_with_same_values_are_equal():
    """
    Comprueba que dos entidades con los mismos valores son iguales.
    """

    first = UnsavedChangesCount(
        connection_name="main",
        unsaved_changes=1,
    )

    second = UnsavedChangesCount(
        connection_name="main",
        unsaved_changes=1,
    )

    assert first == second


def test_entity_repr_contains_values():
    """
    Comprueba que la representación de la entidad contiene sus valores.
    """

    entity = UnsavedChangesCount(
        connection_name="main",
        unsaved_changes=2,
    )

    representation = repr(entity)

    assert "main" in representation
    assert "2" in representation

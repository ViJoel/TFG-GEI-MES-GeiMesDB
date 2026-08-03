from entities.navigation_tree_action import NavigationTreeAction

# =============================================================================
# TESTS
# =============================================================================


def test_values_are_generated_as_expected():
    """
    Verifica que los valores generados por StrEnum
    coinciden con sus nombres en minúsculas.
    """

    assert NavigationTreeAction.INSERT_SQL_IN_EDITOR == "insert_sql_in_editor"
    assert NavigationTreeAction.EXECUTE_SQL == "execute_sql"


def test_members_exist():
    """
    Verifica que el enum expone todas las acciones
    soportadas por el árbol de navegación.
    """

    assert list(NavigationTreeAction) == [
        NavigationTreeAction.INSERT_SQL_IN_EDITOR,
        NavigationTreeAction.EXECUTE_SQL,
    ]
